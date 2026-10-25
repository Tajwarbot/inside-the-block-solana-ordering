"""Hard spend cap. Every transaction reserves its WORST-CASE fee before it is sent; the reservation is
never released (a tx that does not land is still counted).

The ledger is GLOBAL per cluster across sessions, so `run --run-dir data/runs/a` and
`run --run-dir data/runs/b` share one budget. The file lives in $OBP_LEDGER_DIR (default: the
parent `data` root), not in the per-session OBP_DATA directory. Read-modify-write is guarded by an
OS file lock (fcntl.flock) so two processes/objects cannot jointly exceed the cap.
ABSOLUTE_CEILING cannot be raised from the CLI or env."""
import fcntl
import json
import os
import threading

LAMPORTS_PER_SOL = 1_000_000_000
ABSOLUTE_CEILING = 50_000_000  # 0.05 SOL, the bounty's budget
BASE_FEE_PER_SIG = 5_000


def worst_case_fee(num_sigs: int, cu_limit: int, cu_price_micro: int) -> int:
    prio = -(-cu_limit * cu_price_micro // 1_000_000)  # ceil
    return BASE_FEE_PER_SIG * num_sigs + prio


def ledger_filename(cluster: str) -> str:
    return f"spend_ledger_{cluster}.json"


def ledger_dir(data_dir: str) -> str:
    """Directory that holds the GLOBAL per-cluster ledger.

    OBP_LEDGER_DIR wins. Otherwise sessions under data/runs/<id> share <...>/data, while the
    default `data` run dir is itself the root. Any other data dir uses its parent, which is the
    conventional root for sibling session directories.
    """
    env = os.environ.get("OBP_LEDGER_DIR")
    if env:
        return env
    d = os.path.abspath(data_dir)
    if os.path.basename(d) == "data":
        return d
    parent = os.path.dirname(d)
    if os.path.basename(parent) == "runs":
        return os.path.dirname(parent)
    return parent


def ledger_path(data_dir: str, cluster: str) -> str:
    return os.path.join(ledger_dir(data_dir), ledger_filename(cluster))


class SpendCapExceeded(RuntimeError):
    pass


class SpendLedger:
    def __init__(self, path: str, cap_lamports: int):
        self.path = path
        self.lock_path = path + ".lock"
        self.cap = min(int(cap_lamports), ABSOLUTE_CEILING)
        self._lock = threading.Lock()
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        self.reserved = self._read()

    def _read(self) -> int:
        if not os.path.exists(self.path):
            return 0
        with open(self.path) as f:
            return int(json.load(f).get("reserved_lamports", 0))

    def _write(self, reserved: int) -> None:
        tmp = self.path + ".tmp"
        with open(tmp, "w") as f:
            json.dump({"reserved_lamports": reserved, "cap_lamports": self.cap}, f)
        os.replace(tmp, self.path)

    def reserve(self, lamports: int, note: str = ""):
        if not isinstance(lamports, int) or isinstance(lamports, bool) or lamports <= 0:
            raise ValueError(f"reservation must be a positive integer number of lamports; got {lamports!r}")
        with self._lock:
            with open(self.lock_path, "a+") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                try:
                    # Re-read inside the OS lock: another session may have reserved meanwhile.
                    self.reserved = self._read()
                    if self.reserved + lamports > self.cap:
                        raise SpendCapExceeded(
                            f"cap {self.cap} lamports; already {self.reserved}; need {lamports} ({note})")
                    self.reserved += lamports
                    self._write(self.reserved)
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def snapshot(self, path: str) -> None:
        """Copy the current global ledger state into a session directory for the commit."""
        with self._lock:
            with open(self.lock_path, "a+") as lock:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
                try:
                    self.reserved = self._read()
                finally:
                    fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump({"reserved_lamports": self.reserved, "cap_lamports": self.cap,
                       "source_ledger": os.path.abspath(self.path)}, f, indent=1)

    @property
    def remaining(self):
        return self.cap - self.reserved

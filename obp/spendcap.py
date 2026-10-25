"""Hard spend cap. Every transaction reserves its WORST-CASE fee before it is sent; the reservation is
never released (a tx that does not land is still counted). The ledger is persisted so restarts can't
reset it. ABSOLUTE_CEILING cannot be raised from the CLI or env."""
import json, os, threading

LAMPORTS_PER_SOL = 1_000_000_000
ABSOLUTE_CEILING = 50_000_000  # 0.05 SOL, the bounty's budget
BASE_FEE_PER_SIG = 5_000


def worst_case_fee(num_sigs: int, cu_limit: int, cu_price_micro: int) -> int:
    prio = -(-cu_limit * cu_price_micro // 1_000_000)  # ceil
    return BASE_FEE_PER_SIG * num_sigs + prio


class SpendCapExceeded(RuntimeError):
    pass


class SpendLedger:
    def __init__(self, path: str, cap_lamports: int):
        self.path = path
        self.cap = min(int(cap_lamports), ABSOLUTE_CEILING)
        self._lock = threading.Lock()
        self.reserved = 0
        if os.path.exists(path):
            with open(path) as f:
                self.reserved = json.load(f).get("reserved_lamports", 0)

    def reserve(self, lamports: int, note: str = ""):
        with self._lock:
            if self.reserved + lamports > self.cap:
                raise SpendCapExceeded(f"cap {self.cap} lamports; already {self.reserved}; need {lamports} ({note})")
            self.reserved += lamports
            tmp = self.path + ".tmp"
            with open(tmp, "w") as f:
                json.dump({"reserved_lamports": self.reserved, "cap_lamports": self.cap}, f)
            os.replace(tmp, self.path)

    @property
    def remaining(self):
        return self.cap - self.reserved

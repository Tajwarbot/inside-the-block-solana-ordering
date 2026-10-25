"""Tiny JSON-RPC client with retries and rate-limit backoff (read-only helpers + sendTransaction)."""
import os, time, json, logging, requests

log = logging.getLogger("obp.rpc")
DEFAULT_RPC = os.environ.get("RPC_URL", "https://api.mainnet-beta.solana.com")


class RpcError(RuntimeError):
    pass


class Rpc:
    def __init__(self, url: str = DEFAULT_RPC, timeout: float = 30.0, max_retries: int = 5):
        self.url, self.timeout, self.max_retries = url, timeout, max_retries
        self.s = requests.Session()
        self._id = 0

    def call(self, method: str, params=None):
        self._id += 1
        body = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []}
        delay = 0.5
        for attempt in range(self.max_retries):
            try:
                r = self.s.post(self.url, json=body, timeout=self.timeout)
                if r.status_code == 429 or r.status_code >= 500:
                    raise RpcError(f"HTTP {r.status_code}")
                j = r.json()
                if "error" in j:
                    err = j["error"]
                    # -32004/-32007/-32009: block not available / skipped / missing; don't retry forever
                    if err.get("code") in (-32004, -32007, -32009):
                        return {"__error__": err}
                    raise RpcError(json.dumps(err))
                return j["result"]
            except (requests.RequestException, RpcError, ValueError) as e:
                if attempt == self.max_retries - 1:
                    raise
                log.debug("%s retry %d after %s", method, attempt + 1, e)
                time.sleep(delay)
                delay = min(delay * 2, 8)

    # convenience wrappers -------------------------------------------------
    def slot(self, commitment="processed"):
        return self.call("getSlot", [{"commitment": commitment}])

    def epoch_info(self):
        return self.call("getEpochInfo")

    def cluster_nodes(self):
        return self.call("getClusterNodes")

    def vote_accounts(self):
        return self.call("getVoteAccounts")

    def leader_schedule(self, slot=None, identity=None):
        cfg = {"identity": identity} if identity else {}
        return self.call("getLeaderSchedule", [slot, cfg])

    def slot_leaders(self, start, limit):
        return self.call("getSlotLeaders", [start, limit])

    def latest_blockhash(self):
        return self.call("getLatestBlockhash", [{"commitment": "confirmed"}])["value"]

    def balance(self, pubkey):
        return self.call("getBalance", [pubkey, {"commitment": "confirmed"}])["value"]

    def block(self, slot, details="full"):
        return self.call("getBlock", [slot, {"encoding": "json", "transactionDetails": details,
                                             "rewards": False, "maxSupportedTransactionVersion": int(os.environ.get("OBP_MAX_TX_VERSION", 1)),
                                             "commitment": "confirmed"}])

    def signature_statuses(self, sigs):
        out = []
        for i in range(0, len(sigs), 256):
            out += self.call("getSignatureStatuses", [sigs[i:i + 256], {"searchTransactionHistory": True}])["value"]
        return out

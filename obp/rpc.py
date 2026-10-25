"""Tiny JSON-RPC client with a deliberately narrow retry policy, plus cluster identification.

Only HTTP 429/5xx, network failures and explicit JSON-RPC rate limits are retried.
Other JSON-RPC errors are raised immediately. sendTransaction is NEVER retried.
"""
import json
import logging
import os
import time

import requests

log = logging.getLogger("obp.rpc")
DEFAULT_RPC = os.environ.get("RPC_URL", "https://api.mainnet-beta.solana.com")

# Genesis hashes are stable cluster identities (mainnet value checked live with getGenesisHash on 2026-10-25).
# An unknown genesis hash counts as "localnet" ONLY if the RPC URL is on localhost; otherwise "unknown",
# and live sending on "unknown" is refused.
CLUSTER_BY_GENESIS = {
    "5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d": "mainnet",
    "EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG": "devnet",
    "4uhcVJyU9pJkvQyS88uRDiswHXSCkY3zQawwpjk2NsNY": "testnet",
}
RATE_LIMIT_CODES = {-32429, -32005}  # common Solana JSON-RPC rate-limit / throttling codes


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1", "0.0.0.0"}


def cluster_name(genesis_hash: str, url: str = "http://127.0.0.1") -> str:
    from urllib.parse import urlparse
    if genesis_hash in CLUSTER_BY_GENESIS:
        return CLUSTER_BY_GENESIS[genesis_hash]
    return "localnet" if (urlparse(url).hostname or "") in LOCAL_HOSTS else "unknown"


def guard_live_cluster(cluster: str, *, live: bool, allow_mainnet: bool) -> None:
    """Mainnet live runs need an extra explicit opt-in, on top of --live."""
    if live and cluster == "unknown":
        raise SystemExit("Refusing to send: unknown cluster (genesis hash not recognised and RPC is not localhost).")
    if live and cluster == "mainnet" and not allow_mainnet:
        raise SystemExit(
            "Refusing to send on mainnet: pass --live --mainnet explicitly "
            "(and make sure the spend cap and payer keys are correct)."
        )


class RpcError(RuntimeError):
    pass


class _Retryable(RpcError):
    pass


class Rpc:
    def __init__(self, url: str = DEFAULT_RPC, timeout: float = 30.0, max_retries: int = 5):
        self.url, self.timeout, self.max_retries = url, timeout, max_retries
        self.s = requests.Session()
        self._id = 0
        self._genesis = None

    def call(self, method: str, params=None, retries: int | None = None):
        if method == "sendTransaction":
            retries = 1  # sending is never safe to retry automatically
        attempts = max(1, self.max_retries if retries is None else retries)
        self._id += 1
        body = {"jsonrpc": "2.0", "id": self._id, "method": method, "params": params or []}
        delay = 0.5
        last: Exception | None = None
        for attempt in range(attempts):
            try:
                r = self.s.post(self.url, json=body, timeout=self.timeout)
                if r.status_code == 429 or r.status_code >= 500:
                    raise _Retryable(f"HTTP {r.status_code}")
                if r.status_code >= 400:
                    raise RpcError(f"HTTP {r.status_code}: {r.text[:200]}")
                try:
                    j = r.json()
                except ValueError as e:
                    raise RpcError(f"invalid JSON response: {e}") from e
                if "error" in j:
                    err = j["error"]
                    code = err.get("code")
                    # Block unavailable / skipped / missing: return a sentinel, do NOT retry.
                    if code in (-32004, -32007, -32009):
                        return {"__error__": err}
                    msg = json.dumps(err)
                    if code in RATE_LIMIT_CODES or "rate limit" in msg.lower() or "too many requests" in msg.lower():
                        raise _Retryable(msg)
                    raise RpcError(msg)
                return j["result"]
            except (requests.RequestException, _Retryable) as e:
                last = e
                if attempt == attempts - 1:
                    break
                log.debug("%s retry %d after %s", method, attempt + 1, e)
                time.sleep(delay)
                delay = min(delay * 2, 8)
        if isinstance(last, _Retryable):
            raise RpcError(str(last))
        raise RpcError(f"network error: {last}")

    # convenience wrappers -------------------------------------------------
    def genesis_hash(self) -> str:
        if self._genesis is None:
            self._genesis = self.call("getGenesisHash")
        return self._genesis

    def cluster(self) -> str:
        return cluster_name(self.genesis_hash(), self.url)

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

    def blocks(self, start, end):
        return self.call("getBlocks", [start, end, {"commitment": "confirmed"}])

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

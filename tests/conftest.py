import pytest


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch):
    """Tests must not depend on the caller's OBP_* / RPC env (e.g. a real ledger dir)."""
    for k in ("OBP_DATA", "OBP_LEDGER_DIR", "OBP_KEYPAIRS", "RPC_URL", "SEND_RPC_URL"):
        monkeypatch.delenv(k, raising=False)

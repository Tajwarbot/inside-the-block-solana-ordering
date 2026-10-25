import json

import pytest

from obp.rpc import CLUSTER_BY_GENESIS, Rpc, RpcError, cluster_name, guard_live_cluster


def test_cluster_name_map():
    assert cluster_name("5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d") == "mainnet"
    assert cluster_name("EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG") == "devnet"
    assert cluster_name("4uhcVJyU9pJkvQyS88uRDiswHXSCkY3zQawwpjk2NsNY") == "testnet"
    assert cluster_name("some-local-genesis") == "localnet"
    assert len(set(CLUSTER_BY_GENESIS.values())) == 3


def test_live_mainnet_requires_explicit_flag():
    with pytest.raises(SystemExit) as exc:
        guard_live_cluster("mainnet", live=True, allow_mainnet=False)
    assert "mainnet" in str(exc.value).lower()
    guard_live_cluster("mainnet", live=True, allow_mainnet=True)
    guard_live_cluster("mainnet", live=False, allow_mainnet=False)
    guard_live_cluster("localnet", live=True, allow_mainnet=False)


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status
        self.text = json.dumps(payload)

    def json(self):
        return self._payload


def test_non_rate_limit_jsonrpc_error_is_not_retried(monkeypatch):
    rpc = Rpc("http://example.invalid", max_retries=5)
    calls = []

    def post(*args, **kwargs):
        calls.append(1)
        return FakeResponse({"jsonrpc": "2.0", "id": 1, "error": {"code": -32602, "message": "bad params"}})

    monkeypatch.setattr(rpc.s, "post", post)
    with pytest.raises(RpcError):
        rpc.call("getSlot")
    assert len(calls) == 1


def test_rate_limit_is_retried(monkeypatch):
    rpc = Rpc("http://example.invalid", max_retries=3)
    responses = [
        FakeResponse({"jsonrpc": "2.0", "id": 1, "error": {"code": -32429, "message": "rate limit"}}),
        FakeResponse({"jsonrpc": "2.0", "id": 2, "result": 123}),
    ]
    monkeypatch.setattr("obp.rpc.time.sleep", lambda *_: None)
    monkeypatch.setattr(rpc.s, "post", lambda *a, **k: responses.pop(0))
    assert rpc.call("getSlot") == 123


def test_send_transaction_is_never_retried(monkeypatch):
    rpc = Rpc("http://example.invalid", max_retries=5)
    calls = []

    def post(*args, **kwargs):
        calls.append(1)
        return FakeResponse({"error": "busy"}, status=429)

    monkeypatch.setattr(rpc.s, "post", post)
    monkeypatch.setattr("obp.rpc.time.sleep", lambda *_: None)
    with pytest.raises(RpcError):
        rpc.call("sendTransaction", ["raw"])
    assert len(calls) == 1


def test_unknown_remote_cluster_refuses_live():
    import pytest
    assert cluster_name("some-genesis", "https://rpc.example.com") == "unknown"
    assert cluster_name("some-genesis", "http://127.0.0.1:8899") == "localnet"
    with pytest.raises(SystemExit):
        guard_live_cluster("unknown", live=True, allow_mainnet=True)


def test_real_mainnet_genesis_hash_is_mainnet():
    # value returned by api.mainnet-beta.solana.com getGenesisHash
    assert cluster_name("5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d", "https://x") == "mainnet"


@pytest.mark.parametrize("method", ["getBlock", "getBlockTime", "getBlocks", "getSlotLeaders"])
def test_missing_slot_sentinel_only_for_read_methods(monkeypatch, method):
    rpc = Rpc("http://example.invalid", max_retries=1)
    payload = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32007, "message": "Slot skipped"}}
    monkeypatch.setattr(rpc.s, "post", lambda *a, **k: FakeResponse(payload))
    assert rpc.call(method)["__error__"]["code"] == -32007


@pytest.mark.parametrize("method", ["sendTransaction", "getSlot", "getSignatureStatuses"])
def test_missing_slot_code_is_an_error_for_other_methods(monkeypatch, method):
    rpc = Rpc("http://example.invalid", max_retries=1)
    payload = {"jsonrpc": "2.0", "id": 1, "error": {"code": -32007, "message": "Slot skipped"}}
    monkeypatch.setattr(rpc.s, "post", lambda *a, **k: FakeResponse(payload))
    with pytest.raises(RpcError):
        rpc.call(method)


def test_expect_signature_rejects_sentinel_and_none():
    from obp.rpc import expect_signature

    assert expect_signature("sig") == "sig"
    for bad in ({"__error__": {"code": -32007}}, None, 123, ["sig"]):
        with pytest.raises(RpcError):
            expect_signature(bad)

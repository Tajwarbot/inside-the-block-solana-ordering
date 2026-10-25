import argparse
from types import SimpleNamespace

import pytest
from solders.hash import Hash
from solders.keypair import Keypair

import obp.__main__ as cli


def test_numeric_cli_validators():
    assert cli._positive_int("5") == 5
    for bad in ("0", "-3", "x"):
        with pytest.raises(argparse.ArgumentTypeError):
            cli._positive_int(bad)

    assert cli._fee_levels("0,1000,1000000") == [0, 1000, 1_000_000]
    for bad in ("0,-1", "0,x", ""):
        with pytest.raises(argparse.ArgumentTypeError):
            cli._fee_levels(bad)

    assert cli._cu_limit("1") == 1
    assert cli._cu_limit("1400000") == 1_400_000
    for bad in ("0", "-1", "1400001", "x"):
        with pytest.raises(argparse.ArgumentTypeError):
            cli._cu_limit(bad)

    assert cli._non_negative_int("0") == 0
    assert cli._non_negative_int("20") == 20
    for bad in ("-1", "x"):
        with pytest.raises(argparse.ArgumentTypeError):
            cli._non_negative_int(bad)


def test_cmd_fund_rejects_non_string_send_result(tmp_path, monkeypatch):
    main, extra = Keypair(), Keypair()
    monkeypatch.setattr(cli, "_load_keys", lambda env, arm: [main, extra])
    monkeypatch.setattr(cli, "DATA", str(tmp_path))

    class FundRpc:
        def cluster(self):
            return "localnet"

        def balance(self, pubkey):
            return 10**12

        def latest_blockhash(self):
            return {"blockhash": str(Hash.default())}

    class BadSendRpc(FundRpc):
        def call(self, *args, **kwargs):
            return {"__error__": {"code": -32007, "message": "Slot skipped"}}

    args = SimpleNamespace(live=True, mainnet=False, lamports=1_000, cap_sol=0.04)
    with pytest.raises(SystemExit, match="1 funding transfer"):
        cli.cmd_fund(args, FundRpc(), BadSendRpc())

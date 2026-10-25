import json

import pytest

from obp.spendcap import (ABSOLUTE_CEILING, SpendCapExceeded, SpendLedger, ledger_filename,
                          ledger_path, worst_case_fee)


def test_worst_case_fee():
    assert worst_case_fee(1, 21_000, 0) == 5_000
    assert worst_case_fee(1, 21_000, 1_000_000) == 26_000
    assert worst_case_fee(2, 21_000, 1_000) == 10_021
    assert worst_case_fee(1, 1, 1) == 5_001  # priority fee rounds up


def test_absolute_ceiling_cannot_be_exceeded(tmp_path):
    led = SpendLedger(str(tmp_path / "ledger.json"), 10**15)
    assert led.cap == ABSOLUTE_CEILING
    led.reserve(ABSOLUTE_CEILING)
    assert led.remaining == 0
    with pytest.raises(SpendCapExceeded):
        led.reserve(1)


def test_reservations_persist(tmp_path):
    path = str(tmp_path / "ledger.json")
    first = SpendLedger(path, 1_000)
    first.reserve(400, "a")
    second = SpendLedger(path, 1_000)
    assert second.reserved == 400
    second.reserve(600, "b")
    assert json.load(open(path))["reserved_lamports"] == 1_000
    with pytest.raises(SpendCapExceeded):
        second.reserve(1, "c")


def test_ledger_is_per_cluster(tmp_path):
    assert ledger_filename("mainnet") == "spend_ledger_mainnet.json"
    assert ledger_filename("localnet") == "spend_ledger_localnet.json"
    mainnet = ledger_path(str(tmp_path), "mainnet")
    localnet = ledger_path(str(tmp_path), "localnet")
    assert mainnet != localnet
    SpendLedger(mainnet, 1_000).reserve(1_000)
    assert SpendLedger(localnet, 1_000).reserved == 0


def test_ledger_dir_defaults_to_shared_parent_data_root(tmp_path, monkeypatch):
    monkeypatch.delenv("OBP_LEDGER_DIR", raising=False)
    root = tmp_path / "data"
    a = root / "runs" / "session_a"
    b = root / "runs" / "session_b"
    pa = ledger_path(str(a), "mainnet")
    pb = ledger_path(str(b), "mainnet")
    assert pa == pb == str(root / "spend_ledger_mainnet.json")
    first, second = SpendLedger(pa, 1_000), SpendLedger(pb, 1_000)
    first.reserve(700)
    with pytest.raises(SpendCapExceeded):
        second.reserve(400)
    second.reserve(300)
    assert SpendLedger(pa, 1_000).reserved == second.reserved == 1_000


def test_ledger_dir_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("OBP_LEDGER_DIR", str(tmp_path / "global"))
    assert ledger_path(str(tmp_path / "session"), "mainnet") == str(
        tmp_path / "global" / "spend_ledger_mainnet.json")


def test_two_ledgers_on_same_file_cannot_jointly_exceed_cap(tmp_path):
    path = str(tmp_path / "spend_ledger_mainnet.json")
    first = SpendLedger(path, 1_000)
    second = SpendLedger(path, 1_000)
    first.reserve(600, "a")
    with pytest.raises(SpendCapExceeded):
        second.reserve(600, "b")  # re-reads 600 inside the lock
    second.reserve(400, "c")
    assert SpendLedger(path, 1_000).reserved == 1_000


def test_snapshot_copies_global_state_into_session(tmp_path):
    path = str(tmp_path / "global" / "spend_ledger_mainnet.json")
    led = SpendLedger(path, 1_000)
    led.reserve(250)
    snap = tmp_path / "session" / "spend_ledger_snapshot.json"
    led.snapshot(str(snap))
    data = json.load(open(snap))
    assert data["reserved_lamports"] == 250
    assert data["source_ledger"] == path

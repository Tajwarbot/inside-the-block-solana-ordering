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

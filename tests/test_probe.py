import csv
import logging

from solders.hash import Hash

from obp.probe import SENT_FIELDS, run_bursts
from obp.spendcap import SpendLedger


class ScriptedRpc:
    def __init__(self, slots):
        self.slots = list(slots)
        self.i = 0

    def slot(self, commitment="processed"):
        value = self.slots[min(self.i, len(self.slots) - 1)]
        self.i += 1
        return value

    def latest_blockhash(self):
        return {"blockhash": str(Hash.default())}


def _run(tmp_path, plan, slots, lead_slots=2):
    sent_csv = tmp_path / "sent.csv"
    ledger = SpendLedger(str(tmp_path / "ledger.json"), 10_000_000)
    rpc = ScriptedRpc(slots)
    run_bursts(rpc, rpc, plan, str(sent_csv), ledger, live=False, keypairs=[], run_id="t",
               fee_levels=[0, 1000], cu_limit=21_000, lead_slots=lead_slots, gap_ms=0)
    return list(csv.DictReader(open(sent_csv, newline="")))


def _plan(*windows):
    return [{"target": "leaderA", "label": "TestClient", "window_start": w} for w in windows]


def test_send_offset_in_window_and_slot_after_send_columns(tmp_path):
    rows = _run(tmp_path, _plan(100), [50, 97, 98, 100])
    assert len(rows) == 2
    for row in rows:
        assert set(SENT_FIELDS) <= set(row)
        assert row["slot_at_send"] == "98"
        assert row["slot_after_send"] == "100"
        assert row["send_offset"] == "-2"
        assert row["in_window_at_send"] == "True"
        assert row["on_time"] == "True"


def test_skip_window_when_previous_burst_is_too_close(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    rows = _run(tmp_path, _plan(100, 104), [50, 97, 98, 99, 100])
    assert [r["window_start"] for r in rows] == ["100", "100"]
    assert "within 8 slots" in caplog.text


def test_far_enough_next_window_is_sent(tmp_path):
    rows = _run(tmp_path, _plan(100, 120), [50, 97, 98, 99, 100, 117, 118, 119])
    assert [r["window_start"] for r in rows] == ["100", "100", "120", "120"]
    assert rows[2]["send_offset"] == "-2"


import pytest
from solders.keypair import Keypair

from obp.probe import SLOT_TIME_S, run_bursts


class DummyLedger:
    remaining = 0

    def __init__(self):
        self.reservations = 0

    def reserve(self, lamports, note=""):
        self.reservations += 1


class LiveRpc(ScriptedRpc):
    def balance(self, pubkey):
        return 10**12

    def call(self, method, params=None, retries=None):
        return "fake-signature"


def test_final_guard_skips_window_without_reserving(tmp_path):
    sent_csv = tmp_path / "sent.csv"
    ledger = DummyLedger()
    rpc = ScriptedRpc([50, 97, 100])  # final wait returns slot 100 >= window_start
    run_bursts(rpc, rpc, _plan(100), str(sent_csv), ledger, live=False, keypairs=[], run_id="t",
               fee_levels=[0, 1000], cu_limit=21_000, lead_slots=3, gap_ms=0)
    assert list(csv.DictReader(open(sent_csv, newline=""))) == []
    assert ledger.reservations == 0


def test_per_tx_estimated_slot_drives_offset_and_on_time(tmp_path, monkeypatch):
    t0 = 1_700_000_000_000_000_000
    step = int(SLOT_TIME_S * 1e9)
    times = iter([t0, t0 + 2 * step, t0 + 5 * step])
    monkeypatch.setattr("obp.probe.time.time_ns", lambda: next(times))

    rows = _run(tmp_path, _plan(100), [50, 90, 96], lead_slots=4)
    assert [r["slot_at_send"] for r in rows] == ["96", "96"]
    assert [r["est_slot_at_send"] for r in rows] == ["98", "101"]
    assert [r["send_offset"] for r in rows] == ["-2", "1"]
    assert [r["on_time"] for r in rows] == ["True", "False"]
    assert [r["send_rank"] for r in rows] == ["0", "1"]


def test_multi_live_requires_one_distinct_payer_per_fee_level(tmp_path):
    ledger = DummyLedger()
    payers = [Keypair() for _ in range(4)]
    with pytest.raises(SystemExit):
        run_bursts(ScriptedRpc([50]), ScriptedRpc([50]), _plan(100), str(tmp_path / "sent.csv"), ledger,
                   live=True, keypairs=payers, run_id="t", fee_levels=[0, 1, 2, 3, 4],
                   cu_limit=21_000, lead_slots=3, send_mode="seq", gap_ms=0, payer_arm="multi")


def test_multi_live_records_unique_payer_count(tmp_path):
    ledger = SpendLedger(str(tmp_path / "ledger.json"), 10_000_000)
    payers = [Keypair() for _ in range(5)]
    rpc = LiveRpc([50, 97, 98, 99])
    run_bursts(rpc, rpc, _plan(100), str(tmp_path / "sent.csv"), ledger, live=True, keypairs=payers,
               run_id="t", fee_levels=[0, 1_000, 10_000, 100_000, 1_000_000],
               cu_limit=21_000, lead_slots=3, send_mode="seq", gap_ms=0, payer_arm="multi")
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 5
    assert {r["n_unique_payers"] for r in rows} == {"5"}
    assert len({r["payer"] for r in rows}) == 5

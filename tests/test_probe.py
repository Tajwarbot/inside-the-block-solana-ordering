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

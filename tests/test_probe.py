import base64
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
        assert row["send_phase"] == "early"
        assert row["burst_late"] == "False"
        assert int(row["send_done_ns"]) >= int(row["send_ts_ns"])
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
        if method == "sendTransaction":
            from solders.transaction import VersionedTransaction

            tx = VersionedTransaction.from_bytes(base64.b64decode(params[0]))
            return str(tx.signatures[0])
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
    assert [r["send_phase"] for r in rows] == ["early", "inside"]
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


class PostSendBoomRpc(LiveRpc):
    def __init__(self, slots, fail_on):
        super().__init__(slots)
        self.calls = 0
        self.fail_on = fail_on

    def slot(self, commitment="processed"):
        self.calls += 1
        if self.calls == self.fail_on:
            raise RuntimeError("post-send getSlot boom")
        return super().slot(commitment)


def test_rows_are_saved_before_a_failing_post_send_get_slot(tmp_path, caplog):
    ledger = SpendLedger(str(tmp_path / "ledger.json"), 10_000_000)
    rpc = PostSendBoomRpc([90, 97, 98, 100], fail_on=4)
    run_bursts(rpc, rpc, _plan(100), str(tmp_path / "sent.csv"), ledger, live=True,
               keypairs=[Keypair()], run_id="t", fee_levels=[0, 1000], cu_limit=21_000,
               lead_slots=2, gap_ms=0)
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 2
    assert all(r["signature"] for r in rows)
    assert all(r["send_result"] == "ok" for r in rows)
    assert all(r["slot_after_send"] == "" for r in rows)
    assert "post-send slot lookup failed" in caplog.text


class BadSendRpc(LiveRpc):
    def call(self, method, params=None, retries=None):
        return {"__error__": {"code": -32007, "message": "Slot skipped"}}


def test_probe_treats_non_string_send_result_as_error(tmp_path):
    rpc = BadSendRpc([90, 97, 98])
    run_bursts(rpc, rpc, _plan(100), str(tmp_path / "sent.csv"), DummyLedger(), live=True,
               keypairs=[Keypair()], run_id="t", fee_levels=[0, 1000], cu_limit=21_000,
               lead_slots=2, gap_ms=0)
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 2
    assert all(r["send_result"].startswith("error:") for r in rows)
    assert all("non-string" in r["send_result"] for r in rows)


def test_alternate_arm_alternates_by_burst_and_records_the_arm(tmp_path):
    ledger = SpendLedger(str(tmp_path / "ledger.json"), 10_000_000)
    payers = [Keypair() for _ in range(5)]
    rpc = LiveRpc([90, 97, 98, 100, 117, 118, 119])
    run_bursts(rpc, rpc, _plan(100, 120), str(tmp_path / "sent.csv"), ledger, live=True,
               keypairs=payers, run_id="t", fee_levels=[0, 1_000, 10_000, 100_000, 1_000_000],
               cu_limit=21_000, lead_slots=2, gap_ms=0, payer_arm="alternate")
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 10
    by_burst = {}
    for r in rows:
        by_burst.setdefault(r["burst"], []).append(r)
    assert {r["payer_arm"] for r in by_burst["0"]} == {"same"}
    assert {r["n_unique_payers"] for r in by_burst["0"]} == {"1"}
    assert {r["payer_arm"] for r in by_burst["1"]} == {"multi"}
    assert {r["n_unique_payers"] for r in by_burst["1"]} == {"5"}


def test_alternate_live_requires_at_least_five_payers(tmp_path):
    payers = [Keypair() for _ in range(4)]
    with pytest.raises(SystemExit):
        run_bursts(ScriptedRpc([50]), ScriptedRpc([50]), _plan(100), str(tmp_path / "sent.csv"),
                   DummyLedger(), live=True, keypairs=payers, run_id="t",
                   fee_levels=[0, 1, 2, 3, 4], cu_limit=21_000, lead_slots=2,
                   send_mode="seq", gap_ms=0, payer_arm="alternate")


def test_fee_level_and_cu_limit_validation():
    from obp.probe import validate_cu_limit, validate_fee_levels

    assert validate_fee_levels([0, 1]) == [0, 1]
    for bad in ([], [-1], [0, -2], [0, 1.5], [0, True]):
        with pytest.raises(ValueError):
            validate_fee_levels(bad)
    assert validate_cu_limit(1) == 1
    assert validate_cu_limit(1_400_000) == 1_400_000
    for bad in (0, -1, 1_400_001, True):
        with pytest.raises(ValueError):
            validate_cu_limit(bad)


def test_calibrate_default_memo_length_matches_a_real_tag(monkeypatch):
    import base64

    from solders.transaction import VersionedTransaction

    from obp.probe import calibrate_cu
    from obp.txbuild import MEMO_PROGRAM, memo_tag

    captured = {}

    class CalRpc:
        def call(self, method, params=None, retries=None):
            captured["tx"] = base64.b64decode(params[0])
            return {"value": {"err": None, "unitsConsumed": 18_000}}

    expected = len(memo_tag(0, 0, 0, 0, "asc"))
    assert expected != 40
    assert calibrate_cu(CalRpc(), str(Keypair().pubkey())) == 18_000
    tx = VersionedTransaction.from_bytes(captured["tx"])
    memo_lengths = [len(bytes(ix.data)) for ix in tx.message.instructions
                    if str(tx.message.account_keys[ix.program_id_index]) == str(MEMO_PROGRAM)]
    assert memo_lengths == [expected]


def test_gap_ms_must_be_non_negative(tmp_path):
    ledger = SpendLedger(str(tmp_path / "ledger.json"), 10_000_000)
    with pytest.raises(ValueError):
        run_bursts(ScriptedRpc([50]), ScriptedRpc([50]), _plan(100), str(tmp_path / "sent.csv"),
                   ledger, live=False, keypairs=[], run_id="t", fee_levels=[0, 1000],
                   cu_limit=21_000, gap_ms=-1)


def test_signatures_are_saved_when_a_later_step_raises(tmp_path, monkeypatch):
    calls = []

    def boom(seconds):
        calls.append(seconds)
        if len(calls) == 2:
            raise RuntimeError("boom after second send")

    monkeypatch.setattr("obp.probe.time.sleep", boom)
    rpc = LiveRpc([90, 92, 98])
    with pytest.raises(RuntimeError, match="boom after second send"):
        run_bursts(rpc, rpc, _plan(100), str(tmp_path / "sent.csv"), DummyLedger(), live=True,
                   keypairs=[Keypair()], run_id="t", fee_levels=[0, 1000], cu_limit=21_000,
                   lead_slots=2, gap_ms=0)
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 2
    assert all(r["signature"] for r in rows)


class WrongSignatureRpc(LiveRpc):
    def call(self, method, params=None, retries=None):
        if method == "sendTransaction":
            return "not-the-expected-signature"
        return super().call(method, params, retries)


def test_probe_rejects_signature_mismatch(tmp_path):
    rpc = WrongSignatureRpc([90, 92, 98, 100])
    run_bursts(rpc, rpc, _plan(100), str(tmp_path / "sent.csv"), DummyLedger(), live=True,
               keypairs=[Keypair()], run_id="t", fee_levels=[0, 1000], cu_limit=21_000,
               lead_slots=2, gap_ms=0)
    rows = list(csv.DictReader(open(tmp_path / "sent.csv", newline="")))
    assert len(rows) == 2
    assert all(r["send_result"].startswith("error:signature-mismatch") for r in rows)


def test_burst_is_marked_late_after_the_window(tmp_path):
    rows = _run(tmp_path, _plan(100), [90, 92, 98, 104])
    assert [r["burst_late"] for r in rows] == ["True", "True"]
    assert [r["send_phase"] for r in rows] == ["early", "early"]

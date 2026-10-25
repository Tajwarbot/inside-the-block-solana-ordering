import csv

from obp.collect import collect
from obp.probe import SENT_FIELDS


def _sent(sig, window_start=100, target="leaderA"):
    row = {f: "" for f in SENT_FIELDS}
    row.update(run="r1", cluster="localnet", burst=0, target=target, label="TestClient",
               window_start=window_start, send_seq=0, order_mode="asc", payer_arm="same",
               cu_price=1000, live="True", send_result="ok", signature=sig)
    return row


def _tx(sig, keys, fee=5000, cu=1000):
    return {"transaction": {"signatures": [sig], "message": {"accountKeys": keys}},
            "meta": {"fee": fee, "computeUnitsConsumed": cu, "err": None}}


class FakeRpc:
    def __init__(self, blocks, statuses, error_slots=()):
        self.blocks_data = blocks
        self.statuses = statuses
        self.error_slots = set(error_slots)
        self.block_calls = []

    def signature_statuses(self, sigs):
        return [self.statuses[s] for s in sigs]

    def block(self, slot, details="full"):
        self.block_calls.append(slot)
        if slot in self.error_slots:
            return {"__error__": {"code": -32007, "message": "Slot skipped"}}
        return self.blocks_data[slot]

    def slot_leaders(self, slot, limit):
        return ["leaderA"]


def _write_sent(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=SENT_FIELDS)
        w.writeheader()
        w.writerows(rows)


def test_collect_is_idempotent_and_records_new_columns(tmp_path):
    sent_csv = tmp_path / "sent.csv"
    landed_csv = tmp_path / "landed.csv"
    blocks_csv = tmp_path / "blocks.csv"
    _write_sent(sent_csv, [_sent("s1"), _sent("s2")])
    fake = FakeRpc(
        blocks={100: {"blockTime": 1234, "transactions": [
            _tx("s1", ["payer"]),
            _tx("other", ["someone"]),
            _tx("s2", ["payer"]),
        ]}},
        statuses={"s1": {"slot": 100, "err": None}, "s2": {"slot": 100, "err": None}},
    )

    collect(fake, str(sent_csv), str(landed_csv), str(blocks_csv))
    collect(fake, str(sent_csv), str(landed_csv), str(blocks_csv))

    assert fake.block_calls == [100]  # second run does not fetch the same slot again
    blocks = list(csv.DictReader(open(blocks_csv)))
    assert len(blocks) == 3  # no duplicated rows
    landed = list(csv.DictReader(open(landed_csv)))
    assert len(landed) == 2
    for row in landed:
        assert row["leader_is_target"] == "True"
        assert row["in_target_window"] == "True"
        assert row["block_time"] == "1234"
        assert row["our_tx_count"] == "2"
        assert row["block_tx_count"] == "3"


def test_collect_handles_skipped_block_error(tmp_path):
    sent_csv = tmp_path / "sent.csv"
    landed_csv = tmp_path / "landed.csv"
    blocks_csv = tmp_path / "blocks.csv"
    _write_sent(sent_csv, [_sent("s3", window_start=101)])
    fake = FakeRpc({}, {"s3": {"slot": 101, "err": None}}, error_slots={101})

    rows = collect(fake, str(sent_csv), str(landed_csv), str(blocks_csv))
    assert len(rows) == 1
    assert rows[0]["slot"] == 101
    assert rows[0]["block_index"] == ""
    assert rows[0]["landed"] is True
    assert list(csv.DictReader(open(blocks_csv))) == []


def test_collect_waits_for_a_recent_live_send(tmp_path, monkeypatch):
    sent_csv = tmp_path / "sent.csv"
    landed_csv = tmp_path / "landed.csv"
    blocks_csv = tmp_path / "blocks.csv"
    row = _sent("s1")
    row["send_ts_ns"] = "999000000000"
    _write_sent(sent_csv, [row])
    fake = FakeRpc(
        blocks={100: {"blockTime": 1234, "transactions": [_tx("s1", ["payer"])]}},
        statuses={"s1": {"slot": 100, "err": None}},
    )
    sleeps = []
    monkeypatch.setattr("obp.collect.time.time", lambda: 1000.0)
    monkeypatch.setattr("obp.collect.time.sleep", lambda sec: sleeps.append(sec))

    collect(fake, str(sent_csv), str(landed_csv), str(blocks_csv), wait_sec=20)

    assert len(sleeps) == 1
    assert abs(sleeps[0] - 19.0) < 1e-6


def test_collect_queries_status_even_when_send_acknowledgement_was_an_error(tmp_path):
    sent_csv = tmp_path / "sent.csv"
    landed_csv = tmp_path / "landed.csv"
    blocks_csv = tmp_path / "blocks.csv"
    row = _sent("s4")
    row["send_result"] = "error:timeout"
    _write_sent(sent_csv, [row])
    fake = FakeRpc(
        blocks={100: {"blockTime": 1234, "transactions": [_tx("s4", ["payer"])]}},
        statuses={"s4": {"slot": 100, "err": None}},
    )

    rows = collect(fake, str(sent_csv), str(landed_csv), str(blocks_csv))
    assert len(rows) == 1
    assert rows[0]["landed"] is True
    assert rows[0]["send_result"] == "error:timeout"

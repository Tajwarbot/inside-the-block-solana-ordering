import csv
import json

from obp.analyze import analyze
from obp.windows import verify_windows


class FakeRpc:
    def __init__(self, finalized):
        self.finalized = finalized
        self.leader_calls = []

    def slot(self, commitment="processed"):
        return self.finalized

    def slot_leaders(self, start, limit):
        self.leader_calls.append(start)
        return ["targetA"] * limit

    def blocks(self, start, end):
        return [start, start + 1, start + 2, start + 3]


def test_only_elapsed_windows_are_verified_and_planned_are_separate(tmp_path):
    plan = tmp_path / "plan.json"
    with open(plan, "w") as f:
        json.dump({"plan": [
            {"window_start": 100, "target": "targetA", "label": "C"},
            {"window_start": 300, "target": "targetA", "label": "C"},
        ]}, f)
    out = tmp_path / "windows.csv"
    rpc = FakeRpc(finalized=200)
    rows = verify_windows(rpc, str(plan), "", str(out))

    assert [r["status"] for r in rows] == ["verified", "planned"]
    assert rows[0]["leaders_ok"] is True
    assert rows[1]["block_count"] == 0
    assert rpc.leader_calls == [100]  # not-yet-elapsed windows are not queried

    text = analyze(str(tmp_path / "missing_landed.csv"), str(tmp_path / "results.csv"),
                   windows_csv=str(out), md_path=str(tmp_path / "results.md"))
    assert "| C | 1 | 1 | 1 | 4 | 1 |" in text

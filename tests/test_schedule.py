from obp.schedule import upcoming_windows


class FakeRpc:
    def __init__(self, now, schedule):
        self.now = now
        self.schedule = schedule

    def epoch_info(self):
        return {"absoluteSlot": self.now, "slotIndex": self.now, "epoch": 1}

    def leader_schedule(self):
        return self.schedule


def test_min_lead_slots_filters_imminent_windows():
    rpc = FakeRpc(now=100, schedule={"A": list(range(0, 201, 4))})

    wins, now = upcoming_windows(rpc, None, horizon_slots=100)
    assert now == 100
    assert wins["A"][0] == 104

    wins, _ = upcoming_windows(rpc, None, horizon_slots=100, min_lead_slots=25)
    assert wins["A"][0] == 128
    assert all(s >= 125 for s in wins["A"])

    wins, _ = upcoming_windows(rpc, None, horizon_slots=100, min_lead_slots=24)
    assert wins["A"][0] == 124  # exactly at now + min_lead_slots is included


def test_min_gap_filter_keeps_the_earliest_window_globally():
    from obp.schedule import min_gap_filter

    candidates = [{"window_start": w, "target": "A"} for w in (120, 104, 100, 112, 116, 108)]
    assert [x["window_start"] for x in min_gap_filter(candidates, 12)] == [100, 112]
    # Round-robin gives B a turn instead of letting A's dense windows take every slot.
    candidates.append({"window_start": 124, "target": "B"})
    assert [x["window_start"] for x in min_gap_filter(candidates, 12)] == [100, 124]


def test_min_gap_filter_zero_keeps_everything_at_distinct_slots():
    from obp.schedule import min_gap_filter

    candidates = [{"window_start": w, "target": "A"} for w in (104, 100, 108)]
    assert [x["window_start"] for x in min_gap_filter(candidates, 0)] == [100, 104, 108]


def test_round_robin_gap_filter_does_not_starve_a_target():
    from obp.schedule import min_gap_filter

    candidates = [{"window_start": w, "target": "A"} for w in (100, 112, 124)]
    candidates += [{"window_start": w, "target": "B"} for w in (101, 113)]
    kept = min_gap_filter(candidates, 12)
    assert {x["target"] for x in kept} == {"A", "B"}
    assert [x["window_start"] for x in kept] == [100, 113]


def test_validate_plan_requires_minimum_targets_and_labels():
    import pytest
    from obp.schedule import validate_plan

    good = [{"target": f"t{i}", "label": f"L{i % 3}", "window_start": 100 + 12 * i} for i in range(6)]
    assert len(validate_plan(good, 6, 3)["targets"]) == 6
    with pytest.raises(SystemExit):
        validate_plan(good[:5], 6, 3)
    with pytest.raises(SystemExit):
        validate_plan([{"target": f"t{i}", "label": "L", "window_start": 100 + i} for i in range(6)], 6, 3)

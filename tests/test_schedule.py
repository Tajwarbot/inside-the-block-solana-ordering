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

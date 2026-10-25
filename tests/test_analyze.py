import csv

from obp.analyze import analyze, kendall, perm_p


def test_kendall_directions_and_ties():
    assert kendall([1, 2, 3], [1, 2, 3]) == 1
    assert kendall([1, 2, 3], [3, 2, 1]) == -1
    assert kendall([1, 1], [1, 2]) is None  # no usable pairs


def test_perm_p_basics():
    assert perm_p([1, 2], [1, 2], None) is None
    p = perm_p([1, 2, 3, 4, 5], [1, 2, 3, 4, 5], 1.0, n=500)
    assert 0 <= p <= 0.1


def test_analyze_survives_dry_run_only_data(tmp_path):
    sent_csv = tmp_path / "sent.csv"
    fields = ["run", "burst", "target", "label", "window_start", "send_seq", "order_mode",
              "payer_arm", "cu_price", "live", "on_time", "in_window_at_send", "send_offset",
              "signature", "send_ts_ns"]
    with open(sent_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for i in range(5):
            w.writerow({"run": "r1", "burst": 0, "target": "t", "label": "DryClient",
                        "window_start": 10, "send_seq": i, "order_mode": "asc", "payer_arm": "same",
                        "cu_price": 1000 * i, "live": "False", "on_time": "True",
                        "in_window_at_send": str(i < 4), "send_offset": -2,
                        "signature": f"s{i}", "send_ts_ns": 1_700_000_000_000_000_000 + i})
    out_csv = tmp_path / "results.csv"
    md_path = tmp_path / "results.md"
    text = analyze(str(tmp_path / "missing_landed.csv"), str(out_csv), sent_csv=str(sent_csv),
                   blocks_csv=str(tmp_path / "missing_blocks.csv"), md_path=str(md_path))
    assert out_csv.exists()
    assert md_path.exists()
    assert "Landing and timing" in text
    assert "on_time rate" in text
    assert "in_window rate" in text
    assert "Verified leader windows" in text
    assert list(csv.DictReader(open(out_csv))) == []


def test_analyze_reports_verified_window_counts_from_windows_csv(tmp_path):
    windows_csv = tmp_path / "windows.csv"
    with open(windows_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "leaders_ok", "block_count"])
        w.writeheader()
        w.writerow({"label": "C", "leaders_ok": "True", "block_count": 4})
        w.writerow({"label": "C", "leaders_ok": "False", "block_count": 0})
    text = analyze(str(tmp_path / "missing_landed.csv"), str(tmp_path / "results.csv"),
                   windows_csv=str(windows_csv), md_path=str(tmp_path / "results.md"))
    assert "## Verified leader windows" in text
    assert "| C | 2 | 1 | 1 | 4 |" in text


def test_analyze_with_landed_and_block_rows(tmp_path):
    from obp.collect import BLOCK_FIELDS, LANDED_FIELDS

    sent_csv = tmp_path / "sent.csv"
    landed_csv = tmp_path / "landed.csv"
    blocks_csv = tmp_path / "blocks.csv"
    with open(sent_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["signature", "run", "burst", "target", "label", "window_start",
                                          "send_seq", "order_mode", "payer_arm", "cu_price", "live", "on_time",
                                          "send_ts_ns"])
        w.writeheader()
        for i in range(5):
            w.writerow({"signature": f"s{i}", "run": "r1", "burst": 0, "target": "t", "label": "C",
                        "window_start": 100, "send_seq": i, "order_mode": "asc", "payer_arm": "same",
                        "cu_price": (i + 1) * 1000, "live": "True", "on_time": "True",
                        "send_ts_ns": 1_700_000_000_000_000_000 + i})
    with open(landed_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LANDED_FIELDS)
        w.writeheader()
        for i in range(5):
            w.writerow({"signature": f"s{i}", "run": "r1", "burst": 0, "target": "t", "label": "C",
                        "window_start": 100, "send_seq": i, "order_mode": "asc", "payer_arm": "same",
                        "cu_price": (i + 1) * 1000, "landed": "True", "slot": 100, "slot_leader": "t",
                        "leader_is_target": "True", "in_target_window": "True", "block_index": i,
                        "block_tx_count": 7, "block_time": 1234, "our_tx_count": 5})
    with open(blocks_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=BLOCK_FIELDS)
        w.writeheader()
        for i in range(5):
            w.writerow({"slot": 100, "block_time": 1234, "index": i, "signature": f"s{i}",
                        "fee": 5000 + (i + 1) * 1000, "cu_consumed": 21_000, "num_sigs": 1,
                        "is_vote": "False", "err": "False"})
    out_csv = tmp_path / "results.csv"
    md_path = tmp_path / "results.md"
    text = analyze(str(landed_csv), str(out_csv), sent_csv=str(sent_csv), blocks_csv=str(blocks_csv),
                   md_path=str(md_path))
    rows = list(csv.DictReader(open(out_csv)))
    assert len(rows) == 1
    assert rows[0]["tau_fee"] not in ("", None)
    assert "Pooled per client label" in text
    assert "Whole-block priority ordering" in text
    assert "Selected sample: our txs in the target window per burst" in text
    assert "| C | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 5 |" in text


def test_results_header_counts_only_landed_true_rows(tmp_path):
    from obp.collect import LANDED_FIELDS

    landed_csv = tmp_path / "landed.csv"
    with open(landed_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LANDED_FIELDS)
        w.writeheader()
        for i in range(5):
            row = {k: "" for k in LANDED_FIELDS}
            row.update(signature=f"s{i}", landed="True" if i < 4 else "False")
            w.writerow(row)
    text = analyze(str(landed_csv), str(tmp_path / "results.csv"), md_path=str(tmp_path / "results.md"))
    assert "- Rows: sent=0, landed=4, block_txs=0" in text
    assert "landed=5" not in text


def test_rates_are_unsigned_and_tau_is_signed():
    from obp.analyze import _fmt, _tau

    assert _fmt(0.8) == "0.800"
    assert _fmt(0.0) == "0.000"
    assert _tau(0.8) == "+0.800"
    assert _tau(-1) == "-1.000"
    assert _tau(None) == "-"


from obp.analyze import _holm, _per_burst


def _landed_rows(label="C", burst=0, target_ok=True, mode="asc", arm="same", slot=100):
    from obp.collect import LANDED_FIELDS
    rows = []
    for i in range(5):
        row = {k: "" for k in LANDED_FIELDS}
        row.update(signature=f"s{label}{burst}{i}", run="r1", burst=burst, target="t",
                   label=label, window_start=slot, send_seq=i, send_rank=i, order_mode=mode,
                   payer_arm=arm, cu_price=(i + 1) * 1000, landed="True", slot=slot,
                   slot_leader="t" if target_ok else "other",
                   leader_is_target=str(target_ok), in_target_window=str(target_ok),
                   block_index=4 - i, block_tx_count=10, block_time=1234, our_tx_count=5)
        rows.append(row)
    return rows


def _write_landed(path, rows):
    from obp.collect import LANDED_FIELDS
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=LANDED_FIELDS)
        w.writeheader(); w.writerows(rows)


def test_primary_stats_exclude_other_leaders_and_sensitivity_keeps_them(tmp_path):
    landed_csv = tmp_path / "landed.csv"
    _write_landed(landed_csv, _landed_rows(burst=0, target_ok=True) +
                  _landed_rows(burst=1, target_ok=False))
    out_csv = tmp_path / "results.csv"
    text = analyze(str(landed_csv), str(out_csv), md_path=str(tmp_path / "results.md"))
    rows = list(csv.DictReader(open(out_csv)))
    assert [r["burst"] for r in rows] == ["0"]
    assert "## Sensitivity: all landed (any leader)" in text
    assert "| C | 2 | 10 |" in text  # sensitivity pooled: 2 bursts, 10 txs


def test_grouped_results_verdicts_and_holm(tmp_path):
    rows = []
    for burst, mode in enumerate(["asc", "desc", "shuffle"]):
        rows += _landed_rows(burst=burst, mode=mode, target_ok=True)
    landed_csv = tmp_path / "landed.csv"
    _write_landed(landed_csv, rows)
    out_csv = tmp_path / "results.csv"
    text = analyze(str(landed_csv), str(out_csv), md_path=str(tmp_path / "results.md"))

    group_csv = tmp_path / "results_by_group.csv"
    grouped = list(csv.DictReader(open(group_csv)))
    assert group_csv.exists()
    assert {r["group_by"] for r in grouped} == {"payer_arm", "order_mode"}
    assert {r["group"] for r in grouped if r["group_by"] == "order_mode"} == {"asc", "desc", "shuffle"}
    assert all(r["txs"] == "5" for r in grouped if r["group_by"] == "order_mode")
    arm = [r for r in grouped if r["group_by"] == "payer_arm"]
    assert len(arm) == 1 and arm[0]["txs"] == "15"
    assert "H1 fee rule" in text
    assert "Holm p" in text


def test_holm_correction_is_monotone_and_capped():
    adjusted = _holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adjusted["a"] == 0.03
    assert adjusted["c"] == 0.06
    assert adjusted["b"] == 0.06
    assert all(v <= 1 for v in adjusted.values())


def test_send_rank_is_used_instead_of_planned_send_seq(tmp_path):
    from obp.collect import LANDED_FIELDS
    rows = []
    for i in range(5):
        row = {k: "" for k in LANDED_FIELDS}
        row.update(signature=f"s{i}", run="r1", burst=0, target="t", label="C", window_start=100,
                   send_seq=4 - i, send_rank=i, order_mode="asc", payer_arm="same",
                   cu_price=(i + 1) * 1000, landed="True", slot=100, slot_leader="t",
                   leader_is_target="True", in_target_window="True", block_index=i)
        rows.append(row)
    _res, bursts = _per_burst(rows)
    assert bursts[0]["seq"] == [0, 1, 2, 3, 4]
    assert bursts[0]["ts"] == 1.0


def _synthetic_burst(label="C", arm="same", mode="desc", fee_dir=1, seq_dir=None, burst=0):
    from obp.analyze import kendall

    idx = list(range(5))
    fee = [-(5 - i) for i in idx] if fee_dir > 0 else [-(i + 1) for i in idx]
    if seq_dir is None:
        # desc sends the highest fee first (aligned); asc sends it last (opposed).
        seq_dir = 1 if mode == "desc" else -1
    seq = idx if seq_dir > 0 else [4 - i for i in idx]
    return {"label": label, "payer_arm": arm, "order_mode": mode, "n": 5,
            "idx": idx, "fee": fee, "seq": seq,
            "tf": kendall(idx, fee), "ts": kendall(idx, seq)}


def _verdict_for(bursts):
    from obp.analyze import _verdicts

    return _verdicts(bursts)[0]["verdict"]


def test_synthetic_rotations_are_aligned_for_desc_and_opposed_for_asc():
    desc = _synthetic_burst(mode="desc")
    asc = _synthetic_burst(mode="asc")
    assert desc["tf"] == desc["ts"] == 1
    assert asc["tf"] * asc["ts"] == -1


def test_verdict_uses_only_same_arm_asc_and_shuffle():
    bursts = [_synthetic_burst(mode="asc", fee_dir=1),
              _synthetic_burst(mode="shuffle", seq_dir=-1, burst=1)]
    # Multi-payer rows would look like H2 if they leaked into the verdict.
    bursts.append(_synthetic_burst(arm="multi", mode="asc", fee_dir=-1, seq_dir=1, burst=2))
    assert _verdict_for(bursts) == "H1 fee rule"


def test_verdict_h2_needs_asc_and_shuffle_send_order():
    bursts = [_synthetic_burst(mode="asc", fee_dir=-1, seq_dir=1),
              _synthetic_burst(mode="shuffle", fee_dir=-1, seq_dir=1, burst=1)]
    assert _verdict_for(bursts) == "H2 arrival rule"


def test_verdict_mixed_and_no_rule_and_desc_is_not_primary():
    both = [_synthetic_burst(mode="asc", fee_dir=1, seq_dir=1),
            _synthetic_burst(mode="shuffle", fee_dir=1, seq_dir=1, burst=1)]
    assert _verdict_for(both).startswith("mixed")
    neither = [_synthetic_burst(mode="asc", fee_dir=-1, seq_dir=-1),
               _synthetic_burst(mode="shuffle", fee_dir=-1, seq_dir=-1, burst=1)]
    assert _verdict_for(neither) == "no rule detected (H0 not rejected)"
    desc_only = [_synthetic_burst(mode="desc", fee_dir=1, seq_dir=1)]
    assert _verdict_for(desc_only) == "insufficient data"

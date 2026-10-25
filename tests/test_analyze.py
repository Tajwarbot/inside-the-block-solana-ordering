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

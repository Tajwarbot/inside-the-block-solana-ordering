"""Offline reproduction: rebuild everything in a temp copy and compare with the committed outputs."""
import filecmp, os, shutil, subprocess, sys
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _strip(path):
    with open(path) as f:
        return [l for l in f if "Analysis generated" not in l]


@pytest.mark.skipif(shutil.which("sha256sum") is None, reason="needs sha256sum")
def test_reproduce_matches_committed(tmp_path):
    pytest.importorskip("matplotlib")
    work = tmp_path / "repo"
    for d in ("obp", "scripts", "data"):
        shutil.copytree(os.path.join(ROOT, d), work / d,
                        ignore=shutil.ignore_patterns("__pycache__", "spend_ledger_*.json"))
    env = dict(os.environ, PY=sys.executable, OBP_LEDGER_DIR=str(tmp_path / "ledger"))
    out = subprocess.run(["bash", "scripts/reproduce.sh"], cwd=work, env=env, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr[-2000:]
    runs = os.path.join(ROOT, "data", "runs")
    checked = 0
    for run in sorted(os.listdir(runs)):
        for name in ("results.csv", "results_by_group.csv", "results.md"):
            ref = os.path.join(runs, run, name)
            if not os.path.exists(ref):
                continue
            new = work / "data" / "runs" / run / name
            if name.endswith(".md"):
                assert _strip(ref) == _strip(new), f"{run}/{name} differs"
            else:
                assert filecmp.cmp(ref, new, shallow=False), f"{run}/{name} differs"
            checked += 1
    assert checked >= 20
    for fig in ("tau_by_label.png", "landing_offset.png", "burst_span.png"):
        assert (work / "figures" / fig).stat().st_size > 10000

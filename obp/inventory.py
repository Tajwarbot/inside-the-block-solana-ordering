"""Build validators.csv: identity, client, version, stake, Jito flags, TPU address. Read-only."""
import csv, logging, requests
from .rpc import Rpc

log = logging.getLogger("obp.inventory")
JITO_API = "https://kobe.mainnet.jito.network/api/v1/validators"
INVENTORY_FIELDS = ["identity", "vote", "stake_sol", "client_id", "version", "label",
                    "running_jito", "running_bam", "tpu_quic"]


def client_label(node: dict, jito: dict | None) -> str:
    """Human label for the scheduler family. clientId comes from gossip (Agave, Firedancer, ...);
    the version string separates Frankendancer (0.x) from full Firedancer; Jito/BAM flags come from Jito's API."""
    cid = node.get("clientId") or "Unknown"
    ver = node.get("version") or ""
    if cid == "Firedancer" and ver.startswith("0."):
        cid = "Frankendancer"
    if jito and jito.get("running_bam") and "BAM" not in cid.upper():
        cid += "+BAM"
    elif jito and jito.get("running_jito") and cid == "Agave":
        cid = "JitoAgave"
    return cid


def build(rpc: Rpc, out_csv: str) -> list[dict]:
    nodes = {n["pubkey"]: n for n in rpc.cluster_nodes()}
    va = rpc.vote_accounts()
    stake_by_node, vote_by_node = {}, {}
    for v in va["current"]:
        stake_by_node[v["nodePubkey"]] = stake_by_node.get(v["nodePubkey"], 0) + v["activatedStake"]
        vote_by_node[v["nodePubkey"]] = v["votePubkey"]
    if not stake_by_node:
        raise SystemExit("no active validators returned by getVoteAccounts; check RPC_URL")
    jito_by_vote = {}
    try:
        for j in requests.get(JITO_API, timeout=30).json().get("validators", []):
            jito_by_vote[j["vote_account"]] = j
    except Exception as e:  # noqa: BLE001 - optional enrichment
        log.warning("Jito API unavailable (%s); Jito flags left blank", e)
    rows = []
    for pk, stake in stake_by_node.items():
        n = nodes.get(pk, {"pubkey": pk})
        j = jito_by_vote.get(vote_by_node.get(pk))
        rows.append({
            "identity": pk, "vote": vote_by_node.get(pk), "stake_sol": round(stake / 1e9, 1),
            "client_id": n.get("clientId"), "version": n.get("version"), "label": client_label(n, j),
            "running_jito": (j or {}).get("running_jito"), "running_bam": (j or {}).get("running_bam"),
            "tpu_quic": n.get("tpuQuic"),
        })
    rows.sort(key=lambda r: -r["stake_sol"])
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=INVENTORY_FIELDS)
        w.writeheader(); w.writerows(rows)
    return rows


def summary(rows):
    agg = {}
    tot = sum(r["stake_sol"] for r in rows) or 1
    for r in rows:
        a = agg.setdefault(r["label"], [0, 0.0, set()])
        a[0] += 1; a[1] += r["stake_sol"]; a[2].add(r["version"])
    return sorted(((k, v[0], round(100 * v[1] / tot, 2), sorted(x for x in v[2] if x)[:4]) for k, v in agg.items()),
                  key=lambda x: -x[2])

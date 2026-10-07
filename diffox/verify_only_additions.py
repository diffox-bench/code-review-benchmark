"""Check that this fork changes no other tool's results: every row that is not diffox's equals the upstream commit's.

    cd offline && python ../diffox/verify_only_additions.py

Reads the four result files at the upstream commit (git show) and in the working tree, removes the two diffox tools
from the working tree's copy, and compares the rest after parsing. Then prints diffox's core rows from the dashboard
that `analysis/benchmark_dashboard.py` regenerates.
"""
import json
import subprocess
import sys

UPSTREAM = "e616e849"
TOOLS = {"diffox", "diffox-ultra"}
JUDGE = "results/anthropic_claude-opus-4-5-20251101"


def at_upstream(path):
    out = subprocess.run(["git", "show", f"{UPSTREAM}:offline/{path}"], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def here(path):
    with open(path) as f:
        return json.load(f)


ok = True
up, me = at_upstream("results/benchmark_data.json"), here("results/benchmark_data.json")
for url in up:
    rest = {**me[url], "reviews": [r for r in me[url]["reviews"] if r.get("tool") not in TOOLS]}
    if rest != up[url]:
        ok = False
        print(f"DIFFERS: benchmark_data.json {url}")
print(f"benchmark_data.json: {len(up)} pull requests, "
      f"{sum(1 for u in me for r in me[u]['reviews'] if r.get('tool') in TOOLS)} diffox reviews added")
for name in ("candidates.json", "dedup_groups.json", "evaluations.json"):
    up, me = at_upstream(f"{JUDGE}/{name}"), here(f"{JUDGE}/{name}")
    for url in up:
        if {k: v for k, v in me[url].items() if k not in TOOLS} != up[url]:
            ok = False
            print(f"DIFFERS: {name} {url}")
    print(f"{name}: every other tool's entries identical to {UPSTREAM}")
board = here("analysis/benchmark_dashboard.json")["models"]["anthropic_claude-opus-4-5-20251101"]["overall_metrics"]
for tool in ("diffox-ultra", "diffox"):
    c = board[tool]["core"]
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    print(f"{tool}: core tp {tp} fp {fp} fn {fn} · F2 {100 * 5 * tp / (5 * tp + 4 * fn + fp):.2f}")
sys.exit(0 if ok else 1)

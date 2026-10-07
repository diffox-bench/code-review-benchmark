#!/bin/bash
# Step 0 as we ran it: Martian's step0_fork_prs.py (this fork's version) once per pull request and product, four at a
# time, with the diffox-bench additions switched on. Each addition is behind its own variable in step0_fork_prs.py.
#
#   GITHUB_TOKEN=<token that can create repositories in the org> BENCH_MIRRORS=<dir of bare mirrors> \
#     diffox/run_copies.sh <jobs.tsv>        # one "<one-PR golden file>\t<tool name>" per line
set -u
cd "$(dirname "$0")/../offline"
export BENCH_KEEP_PRIVATE=1 BENCH_QUIET_REFERENCES=1 BENCH_AVOID_HOUR_START=1
one() {
  uv run --frozen python -m code_review_benchmark.step0_fork_prs --file "$1" --org diffox-bench --name "$2"
}
export -f one
tr '\t' '\n' < "$1" | xargs -n 2 -P 4 bash -c 'one "$0" "$1"'

#!/bin/bash
# Steps 1-3 and the dashboard as we ran them: Martian's own scripts, unmodified, under the board's judge id, so the
# results land in results/anthropic_claude-opus-4-5-20251101/. The calls go to Anthropic's OpenAI-compatible API through
# model_alias_proxy.py, which only removes the "anthropic/" prefix Anthropic's API does not use.
#
#   ANTHROPIC_API_KEY=... GH_TOKEN=<token that can read the copies> diffox/run_scoring.sh
set -eu
cd "$(dirname "$0")/../offline"
python ../diffox/model_alias_proxy.py 8796 & PROXY=$!
trap 'kill $PROXY' EXIT
export MARTIAN_API_KEY="$ANTHROPIC_API_KEY" MARTIAN_BASE_URL=http://127.0.0.1:8796/v1 \
       MARTIAN_MODEL=anthropic/claude-opus-4-5-20251101
uv run --frozen python -m code_review_benchmark.step1_download_prs --org diffox-bench --output results/benchmark_data.json
for tool in diffox diffox-ultra; do
  uv run --frozen python -m code_review_benchmark.step2_extract_comments --tool "$tool"
  uv run --frozen python -m code_review_benchmark.step2_extract_comments --tool "$tool"   # picks up any failed extraction
  uv run --frozen python -m code_review_benchmark.step2_5_dedup_candidates --tool "$tool"
  uv run --frozen python -m code_review_benchmark.step3_judge_comments --tool "$tool"
done
uv run --frozen python analysis/benchmark_dashboard.py

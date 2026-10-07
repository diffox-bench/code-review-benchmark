# diffox on the Code Review Benchmark — our own run of the public harness

This fork of [withmartian/code-review-benchmark](https://github.com/withmartian/code-review-benchmark) adds one run of
**diffox** and **diffox ultra**, made by the diffox team on 2026-10-07 with Martian's own harness at commit `e616e849`.
It is **not an official Martian listing**: Martian has not reviewed or verified it. The benchmark invites exactly this —
*"the harness is public and you're welcome to run it and publish your own results."*

## Result

Offline set: 50 pull requests, 158 core golden comments. Judge: Claude Opus 4.5 (`anthropic_claude-opus-4-5-20251101`).
Core profile, F2 (the board's default score):

| F2 rank | Tool | F2 | F1 | Precision | Recall | TP | FP | FN |
|---|---|---|---|---|---|---|---|---|
| **1** | **diffox ultra** | **66.5** | 56.5 | 45.2% | 75.3% | 119 | 144 | 39 |
| 2 | Qodo Extended | 65.1 | 65.8 | 67.1% | 64.6% | 102 | 50 | 56 |
| 3 | Cubic v2 | 64.9 | 63.6 | 61.5% | 65.8% | 104 | 65 | 54 |
| 4 | Augment | 64.0 | 62.2 | 59.5% | 65.2% | 103 | 70 | 55 |
| **5** | **diffox** | **60.9** | 53.5 | 44.5% | 67.1% | 106 | 132 | 52 |
| 6 | Qodo v2 | 60.6 | 58.5 | 55.4% | 62.0% | 98 | 79 | 60 |

Every other tool's numbers are the published board's, read on 2026-10-07. On F1 (β = 1) diffox ultra ranks 5th and
diffox 7th of the 23.

## Check it yourself

```bash
git clone https://github.com/diffox-bench/code-review-benchmark && cd code-review-benchmark/offline
uv sync --frozen
uv run python analysis/benchmark_dashboard.py          # Martian's own dashboard script, now with our two rows
git diff --diff-algorithm=histogram e616e849 -- results  # additions only: no other tool's line changes
python ../diffox/verify_only_additions.py              # the same, row by row after parsing
```

* **Every review is a pull request you can open.** [diffox/copies.md](diffox/copies.md) lists the 100 copies (50 per
  product), each with exactly one comment by `diffoxai[bot]` and a link to the original pull request.
* **The scoring reproduces the board.** Martian's dashboard script, run over this repository's result files,
  reproduces the published core numbers of 20 of the 21 other tools exactly. The 21st, Gitar, is on the published board
  but has no result files at `e616e849`.

## How the reviews were produced

1. **Step 0** copied each benchmark pull request into its own repository in the `diffox-bench` organization, once per
   product: 100 copies, each with the original title, description, base and head.
2. **The live diffox GitHub App** reviewed each copy once, as it reviews a customer's pull request, in *benchmark
   posting mode*: one plain numbered comment carrying the findings the product publishes, without the badges, summary
   table and list of held-back findings of its normal comment. Step 1 downloads everything a bot writes, and those
   surfaces would otherwise be extracted as extra candidates.
3. **Steps 1, 2, 2.5 and 3 ran unmodified** with `MARTIAN_MODEL=anthropic/claude-opus-4-5-20251101`, so the results sit
   in the board's own results directory. The calls went to Anthropic's OpenAI-compatible API through
   [diffox/model_alias_proxy.py](diffox/model_alias_proxy.py), which only removes the `anthropic/` prefix that
   Anthropic's API does not use for the same model. One extraction returned malformed JSON and was re-run;
   deduplication and judging had no errors. The scripts: [diffox/run_copies.sh](diffox/run_copies.sh),
   [diffox/run_scoring.sh](diffox/run_scoring.sh).

## What differs from Martian's own copies

All of it is in [step0_fork_prs.py](offline/code_review_benchmark/step0_fork_prs.py), each change behind its own
environment variable (`git diff e616e849 -- offline/code_review_benchmark`):

* **No Dependabot.** One commit on each copy's *base* branch removes `.github/dependabot.yml`: Dependabot runs even
  with Actions disabled and would have opened pull requests in the copies. The pull request under review is unchanged.
* **Quiet descriptions.** `@mentions` and links to other issues in copied descriptions are put in code spans, so the
  copies notify nobody and leave no backlinks on the original projects. The words are unchanged.
* **Private until published.** The copies were private while the run was measured and were made public together.
* **Local mirrors** for cloning, and **no pull request opened in the first minutes of an hour**, when our service
  accepts connections late. Neither changes what is reviewed.

## Caveats

* **One run**, as for every tool on the board. Internal replays of the same configuration read 66.7–66.8 F2 for
  diffox ultra.
* **Calibration.** diffox's publication step — which candidate findings get posted — was fitted on this benchmark's
  labelled findings. The reviews themselves are fresh: the copies were reviewed for the first time on 2026-10-07.
* **Edited comments.** Each comment shows as *edited*: the App posts a "Reviewing…" placeholder and replaces it with
  the review when it finishes, about a minute later. GitHub's edit history shows both versions and their times; no
  comment was edited after that.
* **What F2 rewards.** F2 weights recall above precision. diffox ultra's lead comes from recall (75%); its precision is
  45%.

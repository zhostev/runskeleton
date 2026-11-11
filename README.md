# RunSkeleton — a governed AI experiment skeleton

**Kiroween 2026 · Category: Skeleton Crew**

RunSkeleton is a reusable skeleton template for **governed AI experiment
runs**. It wraps any experiment in a thin, strict layer of governance:

- every run is **proposed** against a written hypothesis before it exists,
- admitted or rejected by a **deterministic gate** (a program, not a vibe),
- executed inside a **fixed folder layout** with its config frozen inside,
- evaluated **pairwise against the current champion**,
- and every step is recorded in an **append-only, hash-chained ledger** —
  no record, no result.

The template ships with two demo applications built on it: an **experiment
ledger viewer** and a **paired-evaluation dashboard**. Both are read-only —
in RunSkeleton, only the gate and the ledger writer may change history, and
even they may only append to it.

## Why a skeleton?

Experiments run from loose scripts fail in predictable ways: the config
that produced a number is gone, the evaluation set quietly changed, a
"result" was never recorded anywhere, the baseline moved mid-comparison.
RunSkeleton is the boring skeleton that makes those failures structurally
hard — and it is deliberately small enough to copy into any project in
minutes.

## Repository layout

```text
.kiro/            Kiro steering, specs, and hooks (never gitignored)
template/         the reusable skeleton: CLI + layout + tests
apps/
  ledger-viewer/          demo app 1
  paired-eval-dashboard/  demo app 2
```

## The template

```bash
# initialize a workspace and a run (appends `run_proposed` to the ledger)
python template/skeleton.py init ./my-workspace --run-id run-20261111-001 \
    --hypothesis "Recipe v5 beats v4 on held-out pairs."

# record events (gate verdicts only from the gate actor)
python template/skeleton.py record ./my-workspace --run-id run-20261111-001 \
    --event gate_verdict --actor gate \
    --data '{"gate": "admission", "verdict": "admitted"}'
python template/skeleton.py record ./my-workspace --run-id run-20261111-001 \
    --event run_completed --actor runner --data '{"dev_score": 0.884}'

# prove nobody rewrote history
python template/skeleton.py verify ./my-workspace
# → ledger OK: 3 entries, hash chain intact

python template/skeleton.py list ./my-workspace
```

`skeleton.py` is Python 3.10+ standard library only — a governance tool
must run anywhere. The workspace it creates:

```text
my-workspace/
  runs/<run_id>/config/run_config.json   # frozen at init, never edited
  runs/<run_id>/outputs/
  ledger/ledger.jsonl                    # append-only, hash-chained
  eval/dev/  eval/sealed/                # sealed = read-only, gate-only
  config/
```

Run the template tests:

```bash
python -m pytest template/tests -q   # 8 tests
```

## The demo apps

Both apps are a single dependency-free `index.html` (inline CSS/JS, sample
data embedded in exactly the shape the skeleton produces). No build step —
just open the file in a browser.

- **`apps/ledger-viewer/`** — renders the append-only ledger as a
  filterable table: filter by event type and gate verdict, free-text
  search, and a stats strip (entries, runs, verdicts, promotions). The
  sample ledger shows the full life-cycle, including an admission
  *rejected* because the run pinned a stale data snapshot, and a promotion
  *rolled back* on negative paired evidence.
- **`apps/paired-eval-dashboard/`** — champion vs challenger on 12 paired
  tasks: per-pair scores and deltas, mean paired Δ, win/loss record, and
  an SVG bar chart of the deltas with the gate's reading of the result.

## How Kiro was used

This project was built spec-first with Kiro, and the artifacts are the
point of the Skeleton Crew category — the skeleton includes its own
governance for how it was built:

- **Specs** — `.kiro/specs/governed-experiment-skeleton/` holds
  `requirements.md` (EARS-style: *WHEN … THE SYSTEM SHALL …*), `design.md`
  (ledger + hash-chain design, CLI surface), and `tasks.md` (the build
  checklist this repo was executed against).
- **Steering** — `.kiro/steering/product.md` (the six non-negotiable
  product rules: no record no result, append-only, sealed stays sealed,
  weights only as training products…), `tech.md` (stdlib-only Python,
  JSONL ledger, single-file apps), and `structure.md` (where every kind of
  file belongs) are loaded into every Kiro session with
  `inclusion: always`, so generated code follows the governance rules
  instead of improvising around them.
- **Hooks** — `.kiro/hooks/run-checks-on-save.json` runs the pytest suite
  whenever a template Python file is edited, and
  `.kiro/hooks/block-sealed-eval-writes.json` blocks any write or commit
  touching `eval/sealed/**` outside the promotion gate — the hook version
  of product rule 4.
- **Vibe coding vs spec mode** — the demo apps' presentation layer was
  vibe-coded against the steering rules, while the ledger core (hash
  chain, gate-actor enforcement) was built strictly from the spec, because
  that is the part whose correctness the whole skeleton stands on.

## Rules the skeleton enforces

1. No record, no result.
2. The ledger is append-only and hash-chained; tampering is detectable.
3. Only the gate writes verdicts; proposers and runners cannot.
4. Sealed evaluation data is read-only outside promotion (hook-enforced).
5. Run IDs are never reused; configs are frozen at initialization.
6. Demo apps and viewers are read-only consumers, always.

## License

MIT — see `LICENSE`. © 2026 Shijun Zhao.

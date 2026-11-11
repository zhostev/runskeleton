# Tasks — Governed Experiment Skeleton

Spec: `governed-experiment-skeleton`

## Template core

- [x] 1. Create repo layout per steering/structure.md, `.kiro/` at root and
      explicitly not gitignored
- [x] 2. Implement `template/skeleton.py`
  - [x] 2.1 `init`: copy layout, create run folder, freeze config, append
        `run_proposed`; refuse duplicate run IDs (R1)
  - [x] 2.2 `record`: single-line append with hash chain; enforce
        proposed-run check and gate-only verdicts (R2, R3)
  - [x] 2.3 `verify`: recompute chain, report first broken index (R2.3)
  - [x] 2.4 `list`: human-readable entry listing with optional run filter
- [x] 3. Ship `template/layout/` (runs / ledger / eval / config) with the
      default `run_config.template.json`
- [x] 4. pytest suite in `template/tests/`: init structure, append + verify
      round-trip, tamper detection, duplicate-ID refusal, gate-actor rule

## Guardrails

- [x] 5. Hook `run-checks-on-save`: run template tests when template
      Python files are edited
- [x] 6. Hook `block-sealed-eval-writes`: block writes/commits touching
      `eval/sealed/**` outside promotion (R4)

## Demo apps

- [x] 7. `apps/ledger-viewer/index.html`: embedded sample ledger, stats
      strip, event/verdict/search filters, table render (R5.1)
- [x] 8. `apps/paired-eval-dashboard/index.html`: embedded paired sample
      data, mean delta + win/loss summary, per-pair table, SVG delta chart
      (R5.2)

## Docs & release

- [x] 9. README: concept, layout, CLI usage, app usage, how Kiro specs /
      steering / hooks were used
- [x] 10. MIT LICENSE (2026, Shijun Zhao)
- [ ] 11. Record a ≤3-minute demo video and complete the Devpost
      submission (project overview, Kiro usage write-up, blog + social
      post) — outside this repo, tracked in the submission draft

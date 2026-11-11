---
inclusion: always
---

# Structure Steering — RunSkeleton

## Repository layout

```text
.
├── .kiro/                      # Kiro workspace: steering, specs, hooks (NEVER gitignored)
│   ├── steering/               # product.md / tech.md / structure.md (this file)
│   ├── specs/                  # one folder per spec: requirements / design / tasks
│   └── hooks/                  # agent hooks (JSON), enforced guardrails
├── template/                   # the reusable skeleton itself
│   ├── skeleton.py             # CLI: init / record / verify / list
│   ├── layout/                 # folder layout copied for a new workspace
│   │   ├── runs/               # one folder per governed run
│   │   ├── ledger/             # append-only ledger lives here
│   │   ├── eval/               # evaluation assets; eval/sealed/ is sealed
│   │   └── config/             # config templates
│   └── tests/                  # pytest tests for the CLI
├── apps/
│   ├── ledger-viewer/          # demo app 1: append-only ledger as a table
│   └── paired-eval-dashboard/  # demo app 2: champion vs challenger pairs
├── README.md
└── LICENSE
```

## Where new things go

- A new governed capability starts as a spec under `.kiro/specs/<name>/`
  (requirements → design → tasks) before code is written.
- New guardrails go in `.kiro/hooks/` as hook JSON, and the rule they
  enforce must also be stated in `product.md`.
- New demo apps go in `apps/<name>/index.html`, single-file, read-only
  consumers of skeleton outputs — apps never write to the ledger.
- Run outputs never live in this repository's root; they live under a
  workspace initialized from `template/layout/`.

## Naming

- Spec folders: kebab-case, noun phrases (`governed-experiment-skeleton`).
- Hook files: kebab-case verb phrases (`block-sealed-eval-writes`).
- Python modules: snake_case. Ledger event types: snake_case verbs
  (`run_proposed`, `gate_verdict`, `run_completed`).

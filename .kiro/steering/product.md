---
inclusion: always
---

# Product Steering — RunSkeleton

RunSkeleton is a reusable skeleton template for **governed AI experiment runs**.
It exists so that an experiment is never just "a script someone ran": every run
is proposed, admitted, executed, evaluated, and adjudicated through records in
an append-only ledger, and no result counts unless it is in the ledger.

## Product rules (non-negotiable)

1. **No record, no result.** Any run, evaluation, or verdict that is not an
   entry in the append-only ledger (`ledger/ledger.jsonl`) does not count and
   must not be reported as a result.
2. **Append-only, hash-chained.** Ledger entries are never edited or deleted.
   Each entry carries the SHA-256 hash of the previous entry, so tampering
   with history is detectable by `skeleton.py verify`.
3. **Roles act, governance decides.** Proposers may propose runs; only a
   deterministic gate (a program, not a model opinion) records admission and
   promotion verdicts. A model session never writes a verdict directly.
4. **Sealed evaluation stays sealed.** Anything under `eval/sealed/` is
   read-only for run code and role sessions. It is opened only at promotion
   time by the gate. Hooks enforce this.
5. **Weights change only as training products.** The skeleton never edits
   model weights directly. A new champion exists only as the output of a
   recorded training run that passed the promotion gate.
6. **Every run is reproducible from its folder.** A run folder contains its
   config, its data snapshot reference, and its ledger trail. If the config
   is not in the folder, the run did not happen under governance.

## What the skeleton provides

- A fixed folder layout for runs, ledger, evaluation, and config.
- A tiny CLI (`template/skeleton.py`) to initialize runs, append ledger
  events, and verify ledger integrity.
- Two demo applications that consume the skeleton's outputs read-only:
  a ledger viewer and a paired-evaluation dashboard.

## What the skeleton is not

- Not a training framework, not an orchestrator, not a scheduler.
- Not a replacement for the experiment's own code — it wraps experiments
  with governance, it does not write them.

## Vocabulary (use these words exactly)

- **run** — one governed experiment execution, identified by `run_id`.
- **hypothesis** — the falsifiable claim a run tests, recorded before it runs.
- **gate** — a deterministic check (admission, promotion) with a verdict.
- **verdict** — `admitted` / `rejected` / `promoted` / `rolled_back`.
- **champion** — the current accepted baseline a challenger is compared to.
- **challenger** — a candidate compared pairwise against the champion.

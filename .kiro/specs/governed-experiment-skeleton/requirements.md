# Requirements — Governed Experiment Skeleton

Spec: `governed-experiment-skeleton`
Status: implemented (template v0.1, Kiroween 2026)

## Introduction

An AI experiment that lives only in a terminal scrollback cannot be trusted,
reproduced, or compared. This spec defines a minimal skeleton that wraps any
experiment run in governance: the run is proposed against a written
hypothesis, admitted by a deterministic gate, executed inside a fixed folder
layout, evaluated against a champion, and adjudicated — with every step
recorded in an append-only, hash-chained ledger. Two read-only demo
applications (a ledger viewer and a paired-evaluation dashboard) prove the
skeleton's outputs are consumable without trusting the producer.

Requirements are written in EARS style (Easy Approach to Requirements
Syntax): *WHEN / IF / WHILE … THE SYSTEM SHALL …*.

## Requirements

### R1 — Run initialization

- R1.1 WHEN a user runs `skeleton.py init <workspace> --run-id <id>`, THE
  SYSTEM SHALL create the run folder `runs/<id>/` containing `config/`,
  `outputs/`, and a copy of the default run config frozen as
  `config/run_config.json`.
- R1.2 WHEN a run is initialized, THE SYSTEM SHALL append a `run_proposed`
  entry to the workspace ledger before any execution artifact exists.
- R1.3 IF a run folder with the same `run_id` already exists, THEN THE
  SYSTEM SHALL refuse to initialize and exit non-zero, because run IDs are
  never reused.

### R2 — Append-only hash-chained ledger

- R2.1 WHEN an event is recorded, THE SYSTEM SHALL append exactly one JSON
  line to `ledger/ledger.jsonl` and SHALL NOT modify any existing line.
- R2.2 WHEN an entry is appended, THE SYSTEM SHALL include `prev_hash` (the
  hash of the previous entry, or the genesis constant for the first entry)
  and `entry_hash = sha256(prev_hash + canonical_json(entry))`.
- R2.3 WHEN `skeleton.py verify` runs, THE SYSTEM SHALL recompute the full
  chain and report the first index at which the chain breaks, or confirm
  integrity.
- R2.4 WHILE a ledger entry exists, THE SYSTEM SHALL treat its `run_id`,
  `event`, `actor`, and `timestamp` fields as immutable facts.

### R3 — Gate verdicts

- R3.1 WHEN a gate evaluates a run, THE SYSTEM SHALL record the outcome as
  a `gate_verdict` ledger entry whose `verdict` is one of `admitted`,
  `rejected`, `promoted`, `rolled_back`.
- R3.2 IF a run has no `run_proposed` entry, THEN THE SYSTEM SHALL refuse
  to record a verdict for it.
- R3.3 THE SYSTEM SHALL record verdicts only when invoked as the gate
  actor (`--actor gate`); role actors (`proposer`, `runner`) SHALL NOT be
  able to write `gate_verdict` entries.

### R4 — Sealed evaluation protection

- R4.1 WHILE the workspace is in use, THE SYSTEM SHALL treat everything
  under `eval/sealed/` as read-only for run code and role sessions.
- R4.2 WHEN a commit or file write touches `eval/sealed/**` outside the
  promotion flow, THE SYSTEM SHALL block it via the
  `block-sealed-eval-writes` hook.

### R5 — Demo applications

- R5.1 THE SYSTEM SHALL provide a ledger viewer that renders ledger
  entries as a filterable table (filter by event type and verdict) from
  embedded sample data, with no build step and no network access.
- R5.2 THE SYSTEM SHALL provide a paired-evaluation dashboard that, WHEN
  given paired champion/challenger scores, SHALL display per-pair deltas,
  the mean delta, and a bar chart of the deltas.
- R5.3 WHILE a demo app is open, THE SYSTEM SHALL NOT write to any ledger;
  demo apps are read-only consumers.

### R6 — Reproducibility

- R6.1 WHEN a run folder is inspected after completion, THE SYSTEM SHALL
  make the run's frozen config and full ledger trail sufficient to state
  what was run, by whom, under which hypothesis, and with what verdict —
  without consulting any external system.

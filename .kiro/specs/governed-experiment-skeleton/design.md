# Design — Governed Experiment Skeleton

Spec: `governed-experiment-skeleton`

## Architecture

Three layers, strictly ordered by trust:

```text
┌─────────────────────────────────────────────────────────┐
│ Demo apps (read-only)                                   │
│  apps/ledger-viewer          apps/paired-eval-dashboard │
│  render ledger entries       render paired deltas       │
├─────────────────────────────────────────────────────────┤
│ Template CLI (template/skeleton.py, stdlib only)        │
│  init ──► record ──► verify          list               │
├─────────────────────────────────────────────────────────┤
│ Workspace (initialized from template/layout/)           │
│  runs/<run_id>/   ledger/ledger.jsonl   eval/   config/ │
└─────────────────────────────────────────────────────────┘
```

The apps never write. The CLI is the only sanctioned writer. The workspace
is plain files — no database server, no daemon — so a workspace can be
tarred, hashed, and archived as evidence.

## Ledger design

One JSON object per line in `ledger/ledger.jsonl`:

```json
{
  "seq": 3,
  "timestamp": "2026-11-11T12:00:00Z",
  "run_id": "run-20261111-001",
  "event": "gate_verdict",
  "actor": "gate",
  "data": {"gate": "admission", "verdict": "admitted"},
  "prev_hash": "9f2c…",
  "entry_hash": "b71a…"
}
```

- `entry_hash = sha256((prev_hash + canonical_json(entry_without_hashes)).encode())`,
  where canonical JSON is `json.dumps(..., sort_keys=True, separators=(",", ":"))`.
- Genesis entry uses `prev_hash = "GENESIS"`.
- Verification is O(n): re-read, recompute, compare. The first mismatch
  index is reported; everything after a break is untrusted by definition.

This is deliberately *not* a blockchain: there is one writer (the CLI) and
the chain exists to make silent history edits evident, not to reach
consensus.

## CLI design (`template/skeleton.py`)

| Command | Effect |
|---|---|
| `init <workspace> --run-id ID [--hypothesis TEXT]` | Copy layout, create run folder + frozen config, append `run_proposed`. Refuses duplicate IDs. |
| `record <workspace> --run-id ID --event EVENT --actor ACTOR [--data JSON]` | Append one entry. Enforces R3.2 (run must be proposed) and R3.3 (only `gate` writes `gate_verdict`). |
| `verify <workspace>` | Recompute hash chain; exit 0 if intact, 1 with first bad index otherwise. |
| `list <workspace> [--run-id ID]` | Print entries as a table (used by humans; the viewer app is the rich UI). |

All commands take the workspace path explicitly — no global state, no
"current workspace" pointer — so scripts cannot silently write to the
wrong ledger.

## Guardrails (hooks)

- `run-checks-on-save` — after a Python file under `template/` is edited,
  run the pytest suite so a broken skeleton is caught at edit time.
- `block-sealed-eval-writes` — before a write/commit touches
  `eval/sealed/**`, block and explain. Sealed data changing silently is
  the exact failure this skeleton exists to prevent.

## Demo app design

Both apps are a single `index.html` with embedded sample data shaped
exactly like real skeleton output (ledger entries for the viewer; paired
results for the dashboard), so swapping the embedded array for a fetched
`ledger.jsonl` export is a data-source change, not a rewrite.

- **Ledger viewer:** stats strip (entries, runs, verdict counts), filters
  (event type, verdict, free-text search), table with hash columns
  truncated for display.
- **Paired-eval dashboard:** summary (mean delta, win/loss count, paired
  count), per-pair table, and an SVG bar chart of deltas with a zero line —
  positive bars (challenger better) vs negative bars.

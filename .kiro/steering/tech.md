---
inclusion: always
---

# Tech Steering — RunSkeleton

## Stack

- **Template CLI:** Python 3.10+, standard library only. No third-party
  dependencies for the skeleton core — a governance tool must run anywhere,
  including air-gapped experiment machines.
- **Ledger format:** JSON Lines (`ledger.jsonl`), one JSON object per line,
  UTF-8, keys sorted. Hash chain: `entry_hash = sha256(prev_hash + canonical_json(entry_without_hash))`.
- **Config format:** JSON (`run_config.json`), copied from
  `template/layout/config/run_config.template.json` at run initialization
  and then frozen inside the run folder.
- **Demo apps:** dependency-free static HTML — a single `index.html` per app
  with inline CSS and JS, sample data embedded as a JS array. No build step,
  no framework, no CDN. Must work from `file://`.
- **Tests:** pytest for the template CLI (`template/tests/`).

## Conventions

- Python code follows PEP 8, type hints on public functions, and every
  public function in `skeleton.py` has a one-line docstring.
- The CLI never mutates an existing ledger entry; the only write operation
  is appending one line. Any code path that would rewrite history is a bug.
- All timestamps are ISO 8601 UTC (`datetime.now(timezone.utc)`), never
  local time, never naive datetimes.
- Run IDs are `run-YYYYMMDD-NNN` (date + zero-padded sequence) unless the
  caller supplies an explicit ID. IDs are never reused.
- Errors are explicit: invalid operations exit non-zero with a message on
  stderr. The CLI never silently skips a failed append.

## Forbidden

- No network calls in the template core or the demo apps.
- No dependencies added to the template core without a spec change.
- No writes to `eval/sealed/**` from run code (enforced by hook).
- No editing of files under a completed run's folder except appending to
  its ledger through the CLI.

#!/usr/bin/env python3
"""RunSkeleton CLI: initialize governed experiment runs and keep their ledger.

Commands:
    init    Create a workspace layout + a run folder, append `run_proposed`.
    record  Append one event to the workspace's append-only ledger.
    verify  Recompute the ledger hash chain and report integrity.
    list    Print ledger entries (optionally filtered by run).

Standard library only. See ../.kiro/specs/governed-experiment-skeleton/.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GENESIS = "GENESIS"
VERDICTS = {"admitted", "rejected", "promoted", "rolled_back"}
LAYOUT_DIRS = ["runs", "ledger", "eval/dev", "eval/sealed", "config"]

DEFAULT_CONFIG: dict[str, Any] = {
    "seed": 42,
    "data_snapshot": "REPLACE_WITH_PINNED_SNAPSHOT_ID",
    "eval_set": "dev",
    "sealed_eval_contact": False,
    "budget": {"max_tokens": 5_000_000, "max_calls": 300, "max_wall_seconds": 1800},
}


def _now() -> str:
    """Current UTC timestamp, ISO 8601 with Z suffix."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _canonical(entry: dict[str, Any]) -> str:
    """Canonical JSON used for hashing: sorted keys, tight separators."""
    return json.dumps(entry, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _entry_hash(prev_hash: str, entry: dict[str, Any]) -> str:
    """SHA-256 over prev_hash + canonical entry (hash fields excluded)."""
    body = {k: v for k, v in entry.items() if k not in ("prev_hash", "entry_hash")}
    return hashlib.sha256((prev_hash + _canonical(body)).encode("utf-8")).hexdigest()


def ledger_path(workspace: Path) -> Path:
    """Path of the workspace's append-only ledger file."""
    return workspace / "ledger" / "ledger.jsonl"


def load_entries(workspace: Path) -> list[dict[str, Any]]:
    """Read all ledger entries in order; empty list if no ledger yet."""
    path = ledger_path(workspace)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_entry(workspace: Path, run_id: str, event: str, actor: str,
                 data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append one hash-chained entry to the ledger and return it."""
    entries = load_entries(workspace)
    prev_hash = entries[-1]["entry_hash"] if entries else GENESIS
    entry: dict[str, Any] = {
        "seq": len(entries) + 1,
        "timestamp": _now(),
        "run_id": run_id,
        "event": event,
        "actor": actor,
        "data": data or {},
        "prev_hash": prev_hash,
    }
    entry["entry_hash"] = _entry_hash(prev_hash, entry)
    path = ledger_path(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(_canonical(entry) + "\n")
    return entry


def verify_chain(workspace: Path) -> tuple[bool, int | None, int]:
    """Verify the hash chain. Returns (ok, first_bad_seq_or_None, entry_count)."""
    entries = load_entries(workspace)
    prev_hash = GENESIS
    for entry in entries:
        if entry.get("prev_hash") != prev_hash:
            return False, entry.get("seq"), len(entries)
        if entry.get("entry_hash") != _entry_hash(prev_hash, entry):
            return False, entry.get("seq"), len(entries)
        prev_hash = entry["entry_hash"]
    return True, None, len(entries)


def _config_template() -> dict[str, Any]:
    """Default run config: layout template file if present, else embedded copy."""
    candidate = Path(__file__).parent / "layout" / "config" / "run_config.template.json"
    if candidate.exists():
        return json.loads(candidate.read_text(encoding="utf-8"))
    return dict(DEFAULT_CONFIG)


def init_run(workspace: Path, run_id: str, hypothesis: str = "") -> Path:
    """Initialize workspace layout and a run folder; append `run_proposed`."""
    run_dir = workspace / "runs" / run_id
    if run_dir.exists():
        raise FileExistsError(f"run folder already exists (run IDs are never reused): {run_dir}")
    for rel in LAYOUT_DIRS:
        (workspace / rel).mkdir(parents=True, exist_ok=True)
    layout_eval_readme = Path(__file__).parent / "layout" / "eval" / "README.md"
    target_readme = workspace / "eval" / "README.md"
    if layout_eval_readme.exists() and not target_readme.exists():
        shutil.copyfile(layout_eval_readme, target_readme)
    (run_dir / "config").mkdir(parents=True)
    (run_dir / "outputs").mkdir()
    config = _config_template()
    config["run_id"] = run_id
    config["hypothesis"] = hypothesis
    (run_dir / "config" / "run_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_entry(workspace, run_id, "run_proposed", "proposer",
                 {"hypothesis": hypothesis})
    return run_dir


def record_event(workspace: Path, run_id: str, event: str, actor: str,
                 data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append an event, enforcing governance rules R3.2 and R3.3."""
    data = data or {}
    entries = load_entries(workspace)
    proposed = any(e["event"] == "run_proposed" and e["run_id"] == run_id for e in entries)
    if event != "run_proposed" and not proposed:
        raise ValueError(f"run {run_id} has no run_proposed entry; refusing to record {event}")
    if event == "gate_verdict":
        if actor != "gate":
            raise PermissionError("only the gate actor may record gate_verdict entries")
        verdict = data.get("verdict")
        if verdict not in VERDICTS:
            raise ValueError(f"verdict must be one of {sorted(VERDICTS)}, got {verdict!r}")
    return append_entry(workspace, run_id, event, actor, data)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(prog="skeleton", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="initialize a run in a workspace")
    p_init.add_argument("workspace")
    p_init.add_argument("--run-id", required=True)
    p_init.add_argument("--hypothesis", default="")

    p_rec = sub.add_parser("record", help="append one ledger event")
    p_rec.add_argument("workspace")
    p_rec.add_argument("--run-id", required=True)
    p_rec.add_argument("--event", required=True)
    p_rec.add_argument("--actor", required=True)
    p_rec.add_argument("--data", default="{}", help="JSON object payload")

    p_ver = sub.add_parser("verify", help="verify the ledger hash chain")
    p_ver.add_argument("workspace")

    p_list = sub.add_parser("list", help="list ledger entries")
    p_list.add_argument("workspace")
    p_list.add_argument("--run-id")

    args = parser.parse_args(argv)
    workspace = Path(args.workspace)
    try:
        if args.command == "init":
            run_dir = init_run(workspace, args.run_id, args.hypothesis)
            print(f"initialized run {args.run_id} at {run_dir}")
        elif args.command == "record":
            entry = record_event(workspace, args.run_id, args.event, args.actor,
                                 json.loads(args.data))
            print(f"recorded seq {entry['seq']} ({entry['event']}) hash {entry['entry_hash'][:12]}…")
        elif args.command == "verify":
            ok, bad, count = verify_chain(workspace)
            if ok:
                print(f"ledger OK: {count} entries, hash chain intact")
                return 0
            print(f"ledger BROKEN at seq {bad}: hash chain mismatch", file=sys.stderr)
            return 1
        elif args.command == "list":
            for e in load_entries(workspace):
                if args.run_id and e["run_id"] != args.run_id:
                    continue
                print(f"{e['seq']:>3}  {e['timestamp']}  {e['run_id']}  "
                      f"{e['event']:<16} {e['actor']:<9} {_canonical(e['data'])}")
    except (FileExistsError, ValueError, PermissionError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

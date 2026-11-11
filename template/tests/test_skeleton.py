"""Tests for the RunSkeleton template CLI (spec: governed-experiment-skeleton)."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import skeleton  # noqa: E402


@pytest.fixture()
def ws(tmp_path: Path) -> Path:
    """A fresh workspace with one initialized run."""
    skeleton.init_run(tmp_path, "run-20261111-001", "Longer training improves held-out score.")
    return tmp_path


def test_init_creates_layout_and_frozen_config(ws: Path) -> None:
    """R1.1: init creates the run folder, layout dirs, and a frozen config."""
    run_dir = ws / "runs" / "run-20261111-001"
    assert (run_dir / "outputs").is_dir()
    config = json.loads((run_dir / "config" / "run_config.json").read_text())
    assert config["run_id"] == "run-20261111-001"
    assert "hypothesis" in config
    for rel in ("ledger", "eval/dev", "eval/sealed", "config"):
        assert (ws / rel).is_dir()


def test_init_appends_run_proposed(ws: Path) -> None:
    """R1.2: the first ledger entry is run_proposed with the genesis prev_hash."""
    entries = skeleton.load_entries(ws)
    assert len(entries) == 1
    assert entries[0]["event"] == "run_proposed"
    assert entries[0]["prev_hash"] == skeleton.GENESIS


def test_init_refuses_duplicate_run_id(ws: Path) -> None:
    """R1.3: run IDs are never reused."""
    with pytest.raises(FileExistsError):
        skeleton.init_run(ws, "run-20261111-001")


def test_append_and_verify_roundtrip(ws: Path) -> None:
    """R2: appended entries keep a valid hash chain."""
    skeleton.record_event(ws, "run-20261111-001", "run_started", "runner")
    skeleton.record_event(ws, "run-20261111-001", "gate_verdict", "gate",
                          {"gate": "admission", "verdict": "admitted"})
    ok, bad, count = skeleton.verify_chain(ws)
    assert ok and bad is None and count == 3


def test_verify_detects_tampering(ws: Path) -> None:
    """R2.3: editing a recorded entry breaks verification at that entry."""
    skeleton.record_event(ws, "run-20261111-001", "run_started", "runner")
    path = skeleton.ledger_path(ws)
    lines = path.read_text().splitlines()
    forged = json.loads(lines[0])
    forged["data"]["hypothesis"] = "rewritten after the fact"
    lines[0] = json.dumps(forged, sort_keys=True)
    path.write_text("\n".join(lines) + "\n")
    ok, bad, _ = skeleton.verify_chain(ws)
    assert not ok and bad == 1


def test_verdict_requires_proposed_run(ws: Path) -> None:
    """R3.2: no verdict for a run that was never proposed."""
    with pytest.raises(ValueError):
        skeleton.record_event(ws, "run-99999999-999", "gate_verdict", "gate",
                              {"verdict": "admitted"})


def test_only_gate_writes_verdicts(ws: Path) -> None:
    """R3.3: role actors cannot write gate_verdict entries."""
    with pytest.raises(PermissionError):
        skeleton.record_event(ws, "run-20261111-001", "gate_verdict", "proposer",
                              {"verdict": "promoted"})


def test_invalid_verdict_rejected(ws: Path) -> None:
    """R3.1: verdict values are a closed set."""
    with pytest.raises(ValueError):
        skeleton.record_event(ws, "run-20261111-001", "gate_verdict", "gate",
                              {"verdict": "looks_fine_to_me"})

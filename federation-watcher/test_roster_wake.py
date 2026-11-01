"""Tests for item 3 (roster-only wake files, inter#271).

route_wake() must write a wake FILE only for a handle the roster resolves —
the union of config.yaml's `watch_mentions` and `load_seat_personas()`'s
personas.conf registry. Every other @token gets exactly one log line and no
file (R1/R2).

Includes mutation checks, ported into this repo's shell-mutant style: apply
a single, verified-exactly-once substitution to a SCRATCH COPY of
watcher.py's source (the real, already-imported `watcher` module is never
touched), import the mutant fresh under its own module name, and confirm it
misbehaves exactly the way the matching unit test above would catch —
printing "KILLED: ... — <test> detects this" the same way the shell suites
do.

Run with:
    python3 federation-watcher/test_roster_wake.py -v
"""
from __future__ import annotations

import importlib.util
import re
import sys
import tempfile
import unittest
from pathlib import Path

WATCHER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(WATCHER_DIR))

import watcher  # noqa: E402

SOURCE = (WATCHER_DIR / "watcher.py").read_text()


def _one_sub(source: str, pattern: str, repl: str) -> str:
    """Apply pattern -> repl exactly once. Asserts the pattern matched
    exactly one spot and the resulting file actually differs — a mutant
    that silently fails to apply (0 or >1 matches, or a no-op edit) proves
    nothing about the real code, so it's a harness bug, not a passing
    mutation check."""
    matches = re.findall(pattern, source)
    assert len(matches) == 1, (
        f"mutation pattern matched {len(matches)} times, expected exactly 1: {pattern!r}"
    )
    mutated, n = re.subn(pattern, repl, source, count=1)
    assert n == 1
    assert mutated != source, "mutation produced an identical file"
    return mutated


def _load_mutant(tmpdir: Path, patched_source: str, name: str):
    """Write `patched_source` to a scratch file under `tmpdir` and import it
    as a module named `name`, independent of (and never touching) the real,
    already-imported `watcher` module."""
    path = tmpdir / f"{name}.py"
    path.write_text(patched_source)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class RosterWakeFileTest(unittest.TestCase):
    """Real (non-mutant) behaviour of route_wake()'s roster filter."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.wake_dir = Path(self.tmp.name) / "wake"
        self.wake_dir.mkdir()
        self.roster = {"qbp-architecture", "deming", "herschel"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_unknown_token_no_wakefile(self):
        """R1: a junk @token (commit sha, @v7, a typo) not in the roster
        gets no wake file, and exactly one log line."""
        line = ('WAKE:MENTION channel=c seq=1 from=qbp-architecture '
                'personas=[\'a7f3c2e\'] snippet="x"')
        logged: list[str] = []
        orig_emit = watcher.emit
        watcher.emit = logged.append
        try:
            watcher.route_wake(self.wake_dir, [], ["a7f3c2e"], line, [], self.roster)
        finally:
            watcher.emit = orig_emit
        self.assertFalse((self.wake_dir / "a7f3c2e").exists())
        self.assertEqual(len(logged), 1)
        self.assertIn("a7f3c2e", logged[0])
        self.assertIn("WAKE:SKIP", logged[0])

    def test_roster_handle_wakefile(self):
        """R2: a real roster handle still gets its wake file written."""
        line = ('WAKE:MENTION channel=c seq=1 from=herschel '
                'personas=[\'deming\'] snippet="x"')
        watcher.route_wake(self.wake_dir, [], ["deming"], line, [], self.roster)
        self.assertTrue((self.wake_dir / "deming").exists())
        self.assertIn(line, (self.wake_dir / "deming").read_text())

    def test_watch_mentions_counts_toward_roster_too(self):
        """resolve_roster() reconciles BOTH sources: a handle only present
        in watch_mentions (no personas.conf entry) is still roster."""
        roster = watcher.resolve_roster(["qbp-architecture", "beekeeper"], None)
        self.assertEqual(roster, {"qbp-architecture", "beekeeper"})

    def test_resolve_roster_unions_personas_conf(self):
        personas_conf = Path(self.tmp.name) / "personas.conf"
        personas_conf.write_text("alpha | ~/Documents/Alpha | AUTO\n")
        roster = watcher.resolve_roster(["beekeeper"], personas_conf)
        self.assertEqual(roster, {"beekeeper", "alpha"})

    def test_escalate_route_gets_a_wakefile_even_though_not_roster(self):
        """deming-escalate is forced to role=to by item 2 (C4) whether or
        not it's a live seat — a cross-item contradiction would be writing
        no file for it while still telling callers it's an unconditional
        wake. route_wake must let it through regardless of roster."""
        line = 'WAKE:MENTION channel=c seq=1 from=qbp-architecture personas=[\'deming-escalate\'] snippet="x"'
        watcher.route_wake(self.wake_dir, [], ["deming-escalate"], line, [], self.roster)
        self.assertTrue((self.wake_dir / "deming-escalate").exists())


class RosterWakeFileMutationTest(unittest.TestCase):
    """Mutation checks: each mutant is built from a verified-single-match
    substitution against the REAL watcher.py source, imported fresh, and
    exercised directly — confirming it misbehaves exactly the way the named
    unit test (above) would catch."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.tmpdir = Path(self.tmp.name)
        self.roster = {"qbp-architecture", "deming", "herschel"}

    def tearDown(self):
        self.tmp.cleanup()

    def test_mutant_write_file_for_any_token_killed_by_R1(self):
        """Mutant: route_wake writes a wake file for every mentioned
        persona, roster or not — the exact R1 regression. The real
        test_unknown_token_no_wakefile asserts no file is written for an
        unknown token, so it fails against this mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r"known = \[p for p in personas if p in roster or p in ALWAYS_TO_HANDLES\]",
            r"known = list(personas)",
        )
        mod = _load_mutant(self.tmpdir, mutated, "watcher_mutant_r1")
        wake_dir = self.tmpdir / "wake"
        wake_dir.mkdir()
        mod.route_wake(wake_dir, [], ["a7f3c2e"], "line", [], self.roster)
        self.assertTrue(
            (wake_dir / "a7f3c2e").exists(),
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: writing a file for any token (roster filter bypassed) "
              "— test_unknown_token_no_wakefile detects this")

    def test_mutant_roster_filter_inverted_killed_by_R2(self):
        """Mutant: the roster membership check feeding `known` is inverted
        (`in roster` -> `not in roster`). A real roster handle like 'deming'
        then gets NO wake file. The real test_roster_handle_wakefile asserts
        it DOES get one, so it fails against this mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r"known = \[p for p in personas if p in roster or p in ALWAYS_TO_HANDLES\]",
            r"known = [p for p in personas if p not in roster]",
        )
        mod = _load_mutant(self.tmpdir, mutated, "watcher_mutant_r2")
        wake_dir = self.tmpdir / "wake"
        wake_dir.mkdir()
        mod.route_wake(wake_dir, [], ["deming"], "line", [], self.roster)
        self.assertFalse(
            (wake_dir / "deming").exists(),
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: roster filter inverted — test_roster_handle_wakefile "
              "detects this")


if __name__ == "__main__":
    unittest.main()

"""Tests for item 2 (three-role mention classification, inter#271).

classify_mention_roles() / classify_roles_for_message() classify every
@handle in a message as `to` / `input` / `cc`, per the beekeeper's ruling
(2026-11-01, narrowed by the architect's sanity-check comment): to > input
> cc, fail-closed to `to` on anything unparseable, and an unconditional `to`
for escalations and beekeeper-sent messages.

Covers the binding matrix rows: C1, C3, C4, and P (the precedence table —
the single test that supersedes the three loose rows C2'/I1/I2 per the
architect's sanity-check comment: "test it once as a single precedence
table ... rather than three loose rows"). Each has a mutation check in this
repo's shell-mutant style, ported to Python (see test_roster_wake.py's
_one_sub/_load_mutant for the shared mechanism).

Run with:
    python3 federation-watcher/test_role_classification.py -v
"""
from __future__ import annotations

import importlib.util
import itertools
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
    matches = re.findall(pattern, source)
    assert len(matches) == 1, (
        f"mutation pattern matched {len(matches)} times, expected exactly 1: {pattern!r}"
    )
    mutated, n = re.subn(pattern, repl, source, count=1)
    assert n == 1
    assert mutated != source, "mutation produced an identical file"
    return mutated


def _load_mutant(tmpdir: Path, patched_source: str, name: str):
    path = tmpdir / f"{name}.py"
    path.write_text(patched_source)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


# ── C1 ────────────────────────────────────────────────────────────────────

class CCGroupTest(unittest.TestCase):
    def test_cc_group_classified_cc(self):
        """C1: a handle inside (cc ...) in the leading block is `cc`; a
        handle in the same leading block but outside the group is `to`."""
        text = "@qbp-architecture (cc @deming) — please review"
        roles = watcher.classify_mention_roles(text)
        self.assertEqual(roles["qbp-architecture"], "to")
        self.assertEqual(roles["deming"], "cc")

    def test_mutant_cc_group_ignored_killed_by_C1(self):
        """Mutant: the leading-block cc-group check is dropped, so every
        leading-block handle (cc'd or not) is classified `to`. The real
        test_cc_group_classified_cc asserts @deming is `cc`, so it fails
        against this mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r"if _in_cc\(pos\):",
            r"if False:",
        )
        mod = _load_mutant(Path(tempfile.mkdtemp()), mutated, "watcher_mutant_c1")
        roles = mod.classify_mention_roles("@qbp-architecture (cc @deming) — please review")
        self.assertEqual(
            roles["deming"], "to",
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: cc-group check dropped (everything in the leading "
              "block classified to) — test_cc_group_classified_cc detects this")


# ── C3 ────────────────────────────────────────────────────────────────────

class FailClosedTest(unittest.TestCase):
    def test_unparseable_fails_to_to(self):
        """C3: no ' — ' separator, or an unclosed '(cc', and EVERY
        mention in the message is `to` — the input classifier never runs
        on that path."""
        no_sep = "@qbp-architecture please handle this, cc @deming for awareness"
        roles = watcher.classify_mention_roles(no_sep)
        self.assertEqual(roles, {"qbp-architecture": "to", "deming": "to"})

        unclosed = "@qbp-architecture (cc @deming — please handle, @herschel can you look"
        roles2 = watcher.classify_mention_roles(unclosed)
        self.assertEqual(
            roles2, {"qbp-architecture": "to", "deming": "to", "herschel": "to"}
        )

    def test_mutant_fail_closed_falls_back_to_input_killed_by_C3(self):
        """Mutant: the fail-closed paths return `input` instead of `to`.
        The real test_unparseable_fails_to_to asserts `to` for every
        mention on an unparseable message, so it fails against this
        mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r'    if sep_idx == -1:\n        return \{h: "to" for h in dict\.fromkeys\(all_handles\)\}\n\n'
            r'    leading = text\[:sep_idx\]',
            '    if sep_idx == -1:\n        return {h: "input" for h in dict.fromkeys(all_handles)}\n\n'
            '    leading = text[:sep_idx]',
        )
        mod = _load_mutant(Path(tempfile.mkdtemp()), mutated, "watcher_mutant_c3")
        roles = mod.classify_mention_roles(
            "@qbp-architecture please handle this, cc @deming for awareness"
        )
        self.assertEqual(
            roles.get("qbp-architecture"), "input",
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: fail-closed path falls back to input instead of to "
              "— test_unparseable_fails_to_to detects this")


# ── C4 ────────────────────────────────────────────────────────────────────

class AlwaysWakeTest(unittest.TestCase):
    def test_escalate_and_beekeeper_always_wake(self):
        """C4: escalation (deming-escalate) and any from=beekeeper message
        always resolve to `to`, even when the text itself would classify
        them as cc."""
        text = "@herschel (cc @deming-escalate) — ship it"
        roles = watcher.classify_roles_for_message(
            text, "qbp-architecture", ["herschel", "deming-escalate"]
        )
        self.assertEqual(roles["deming-escalate"], "to")

        text2 = "@herschel (cc @deming) — ship it"
        roles2 = watcher.classify_roles_for_message(
            text2, "beekeeper", ["herschel", "deming"]
        )
        self.assertEqual(roles2["deming"], "to")
        self.assertEqual(roles2["herschel"], "to")

    def test_mutant_force_to_override_removed_killed_by_C4(self):
        """Mutant: the unconditional-to override for escalate/beekeeper is
        disabled, so a cc'd handle in a beekeeper message stays `cc`. The
        real test_escalate_and_beekeeper_always_wake asserts `to`, so it
        fails against this mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r"if force_to or p in ALWAYS_TO_HANDLES:",
            r"if False:",
        )
        mod = _load_mutant(Path(tempfile.mkdtemp()), mutated, "watcher_mutant_c4")
        roles = mod.classify_roles_for_message(
            "@herschel (cc @deming) — ship it", "beekeeper", ["herschel", "deming"]
        )
        self.assertEqual(
            roles.get("deming"), "cc",
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: escalate/beekeeper force-to override disabled — "
              "test_escalate_and_beekeeper_always_wake detects this")


# ── P: precedence table (supersedes C2'/I1/I2) ──────────────────────────────

ROLE_SIGNALS = ("to", "input", "cc")  # leading-outside-cc, body, leading-cc-group


def _compose_message(signals: tuple[str, ...]) -> str:
    """Build a message where @seat appears in exactly the leading/body
    positions named by `signals` (a non-empty subset of {"to","input","cc"}),
    so classify_mention_roles() sees every combination the precedence table
    has to resolve for one handle in one message."""
    leading_bits = []
    if "to" in signals:
        leading_bits.append("@seat")
    if "cc" in signals:
        leading_bits.append("(cc @seat)")
    leading = " ".join(leading_bits) if leading_bits else "@other"
    body = "@seat please weigh in" if "input" in signals else "no body mentions here"
    return f"{leading} — {body}"


_EXPECTED_ROLE = {
    frozenset({"to"}): "to",
    frozenset({"input"}): "input",
    frozenset({"cc"}): "cc",
    frozenset({"to", "input"}): "to",
    frozenset({"to", "cc"}): "to",
    frozenset({"input", "cc"}): "input",
    frozenset({"to", "input", "cc"}): "to",
}


class RolePrecedenceTest(unittest.TestCase):
    def test_role_precedence(self):
        """P: all 7 non-empty combinations of {to, input, cc} for one
        handle in one message resolve per to > input > cc. Supersedes the
        architect's original C2' row ("cc + body -> to") and the beekeeper's
        I1/I2 rows, per the architect's sanity-check comment: tested once,
        as a single precedence table, rather than three loose rows."""
        combos = [
            frozenset(c)
            for n in range(1, 4)
            for c in itertools.combinations(ROLE_SIGNALS, n)
        ]
        self.assertEqual(len(combos), 7)
        for combo in combos:
            msg = _compose_message(tuple(combo))
            roles = watcher.classify_mention_roles(msg)
            self.assertEqual(
                roles.get("seat"), _EXPECTED_ROLE[combo],
                f"combo={sorted(combo)} message={msg!r} roles={roles}",
            )

    def test_mutant_precedence_pair_out_of_order_killed_by_P(self):
        """Mutant: input is allowed to override an already-set `to`
        (precedence pair out of order — input beats to instead of losing to
        it). test_role_precedence's to+input and to+input+cc rows (which
        expect `to`) fail against this mutant. KILLED."""
        mutated = _one_sub(
            SOURCE,
            r'        if roles\.get\(h\) != "to":\n            roles\[h\] = "input"  # overrides a \'cc\', never a \'to\'',
            '        roles[h] = "input"  # BUG: overrides \'to\' too',
        )
        mod = _load_mutant(Path(tempfile.mkdtemp()), mutated, "watcher_mutant_p")
        roles = mod.classify_mention_roles(_compose_message(("to", "input")))
        self.assertEqual(
            roles.get("seat"), "input",
            "mutant did not misbehave as expected — mutation harness not "
            "exercising the intended path",
        )
        print("KILLED: input allowed to override to (precedence pair out "
              "of order) — test_role_precedence detects this")


if __name__ == "__main__":
    unittest.main()

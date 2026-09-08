"""Tests for the federation-watcher monitor-liveness heartbeat
(crash-recovery R3 / inter#91).

Spawns real (throwaway) `tail -f` child processes to stand in for a seat's
armed §2.i Monitor, and kills them to simulate a dead Monitor — the exact
liveness signal check_monitor_alive() reads via pgrep. Everything runs
against temp directories; never touches ~/.federation-watcher/ for real.

Run with:
    python3 federation-watcher/test_heartbeat.py -v
"""

import importlib
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

WATCHER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(WATCHER_DIR))

import watcher  # noqa: E402


PERSONAS_CONF_FIXTURE = """\
# Federation terminal registry — consumed by launch-federation.sh
# persona            | workdir                      | session_id
alpha                | ~/Documents/Alpha  | AUTO
beta                 | ~/Documents/Beta   | AUTO
deming-test          | ~/Documents        | AUTO

# ─── ADVISERS — consulted, NOT launched ───
#   gemini   | Gemini MCP | Edda architecture adviser
"""


def _wait_for_pgrep(wake_path: Path, want_running: bool, timeout: float = 3.0) -> None:
    """pgrep needs the child process to actually be scheduled; poll briefly
    instead of a fixed sleep so the test isn't flaky under load."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        alive = watcher.check_monitor_alive(wake_path.parent, wake_path.name)
        if bool(alive) == want_running:
            return
        time.sleep(0.05)


class HeartbeatTest(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="watcher-heartbeat-test-")
        self.wake_dir = Path(self.tmpdir) / "wake"
        self.wake_dir.mkdir()
        self.personas_conf = Path(self.tmpdir) / "personas.conf"
        self.personas_conf.write_text(PERSONAS_CONF_FIXTURE)
        self.status_file = Path(self.tmpdir) / "monitor-liveness.json"
        self._procs: list[subprocess.Popen] = []
        # deming-test's own wake file must pre-exist so write_wake() can
        # append to it (ensure_wake_file handles creation, but touch here
        # too so the "own wake file never touched" assertions are clean).
        for persona in ("alpha", "beta", "deming-test"):
            (self.wake_dir / persona).touch()

    def tearDown(self):
        for p in self._procs:
            p.terminate()
            try:
                p.wait(timeout=2)
            except subprocess.TimeoutExpired:
                p.kill()

    def _arm_monitor(self, persona: str) -> subprocess.Popen:
        wake_path = self.wake_dir / persona
        proc = subprocess.Popen(["tail", "-f", "-n", "0", str(wake_path)])
        self._procs.append(proc)
        _wait_for_pgrep(wake_path, want_running=True)
        return proc

    def _kill_monitor(self, proc: subprocess.Popen, persona: str) -> None:
        proc.terminate()
        proc.wait(timeout=2)
        _wait_for_pgrep(self.wake_dir / persona, want_running=False)

    # ── roster parsing ──────────────────────────────────────────────────

    def test_load_seat_personas_skips_comments_and_advisers(self):
        personas = watcher.load_seat_personas(self.personas_conf)
        self.assertEqual(personas, ["alpha", "beta", "deming-test"])
        self.assertNotIn("gemini", personas)

    # ── liveness probe ──────────────────────────────────────────────────

    def test_alive_and_dead_probe(self):
        proc = self._arm_monitor("alpha")
        self.assertTrue(watcher.check_monitor_alive(self.wake_dir, "alpha"))
        self.assertFalse(watcher.check_monitor_alive(self.wake_dir, "beta"))
        self._kill_monitor(proc, "alpha")

    # ── sweep + notification behavior ───────────────────────────────────

    def test_dead_monitor_flagged_on_first_sweep(self):
        """beta never had a Monitor armed — must be flagged within one sweep."""
        self._arm_monitor("alpha")
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", {}
        )
        self.assertFalse(state["beta"]["alive"])
        self.assertTrue(state["alpha"]["alive"])

        notify_lines = (self.wake_dir / "deming-test").read_text().splitlines()
        dead_lines = [l for l in notify_lines if "MONITOR_DEAD persona=beta" in l]
        self.assertEqual(len(dead_lines), 1)

    def test_healthy_seat_gets_zero_wake_noise(self):
        """Alive seats must not have anything written to their OWN wake file
        by the heartbeat — only the notify_persona gets the flag line."""
        self._arm_monitor("alpha")
        watcher.run_heartbeat_sweep(self.wake_dir, self.personas_conf, "deming-test", {})
        alpha_lines = (self.wake_dir / "alpha").read_text().splitlines()
        self.assertEqual(alpha_lines, [], "healthy seat's own wake file must stay untouched")

    def test_kill_monitor_flags_transition_within_one_sweep(self):
        """The AC's literal scenario: kill a seat's monitor -> watcher flags
        it within one interval (one run_heartbeat_sweep call)."""
        proc = self._arm_monitor("alpha")
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", {}
        )
        self.assertTrue(state["alpha"]["alive"])
        before = (self.wake_dir / "deming-test").read_text().splitlines()
        self.assertFalse(any("persona=alpha" in l for l in before))

        self._kill_monitor(proc, "alpha")
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", state
        )
        self.assertFalse(state["alpha"]["alive"])
        after = (self.wake_dir / "deming-test").read_text().splitlines()
        dead_lines = [l for l in after if "MONITOR_DEAD persona=alpha" in l]
        self.assertEqual(len(dead_lines), 1)

    def test_no_repeat_notify_while_still_dead(self):
        """A seat dead across multiple sweeps gets exactly one flag, not one
        per interval — low overhead / no notify-spam to deming."""
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", {}
        )
        first_count = len([
            l for l in (self.wake_dir / "deming-test").read_text().splitlines()
            if "MONITOR_DEAD persona=beta" in l
        ])
        self.assertEqual(first_count, 1)

        for _ in range(3):
            state = watcher.run_heartbeat_sweep(
                self.wake_dir, self.personas_conf, "deming-test", state
            )
        second_count = len([
            l for l in (self.wake_dir / "deming-test").read_text().splitlines()
            if "MONITOR_DEAD persona=beta" in l
        ])
        self.assertEqual(second_count, 1, "repeated dead state must not re-notify")

    def test_recovery_flagged(self):
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", {}
        )
        self.assertFalse(state["beta"]["alive"])

        proc = self._arm_monitor("beta")
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", state
        )
        self.assertTrue(state["beta"]["alive"])
        lines = (self.wake_dir / "deming-test").read_text().splitlines()
        recovered = [l for l in lines if "MONITOR_RECOVERED persona=beta" in l]
        self.assertEqual(len(recovered), 1)
        self._kill_monitor(proc, "beta")

    def test_status_file_roundtrip(self):
        state = watcher.run_heartbeat_sweep(
            self.wake_dir, self.personas_conf, "deming-test", {}
        )
        watcher.save_heartbeat_state(self.status_file, state)
        reloaded = watcher.load_heartbeat_state(self.status_file)
        self.assertEqual(reloaded["beta"]["alive"], False)
        self.assertIn("last_checked", reloaded["beta"])
        self.assertIn("since", reloaded["beta"])


if __name__ == "__main__":
    unittest.main()

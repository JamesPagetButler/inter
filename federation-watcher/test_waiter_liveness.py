"""inter#271 follow-up: the heartbeat must recognise wake-wait.sh waiters.

After seats moved off the 30-min Monitor onto wake-wait.sh (inter#157), the
tail-only probe reported every seat MONITOR_DEAD. check_monitor_alive now
accepts (1) a live wake-wait.sh pidfile, (2) an offset advanced within the
re-arm grace window, or (3) the legacy tail Monitor.
"""
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import watcher  # noqa: E402


class WaiterLivenessTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.wake = self.root / "wake"
        self.state = self.root / "state"
        self.wake.mkdir()
        self.state.mkdir()
        (self.wake / "alpha").touch()
        self.procs = []

    def tearDown(self):
        for p in self.procs:
            p.kill()
            p.wait()

    def _fake_waiter(self, persona):
        # a process whose argv contains "wake-wait.sh <persona>", like the real one
        script = self.root / "wake-wait.sh"
        script.write_text("sleep 30\n")
        p = subprocess.Popen(["bash", str(script), persona])
        self.procs.append(p)
        time.sleep(0.2)
        return p.pid

    def test_waiter_pidfile_counts_as_alive(self):
        pid = self._fake_waiter("alpha")
        (self.state / "alpha.waiter.pid").write_text(f"{pid}\n")
        self.assertTrue(watcher.check_monitor_alive(self.wake, "alpha"))

    def test_waiter_for_other_persona_not_alive(self):
        pid = self._fake_waiter("beta")
        (self.state / "alpha.waiter.pid").write_text(f"{pid}\n")
        self.assertFalse(watcher.check_monitor_alive(self.wake, "alpha"))

    def test_stale_pidfile_not_alive(self):
        (self.state / "alpha.waiter.pid").write_text("999999\n")
        old = self.state / "alpha.offset"
        old.write_text("1\n")
        past = time.time() - 3600
        os.utime(old, (past, past))
        self.assertFalse(watcher.check_monitor_alive(self.wake, "alpha"))

    def test_recent_offset_within_grace_counts_as_alive(self):
        (self.state / "alpha.offset").write_text("1\n")  # just fired; seat mid-turn
        self.assertTrue(watcher.check_monitor_alive(self.wake, "alpha"))


def _mutation_checks():
    """Mutants that must be KILLED: dropping the waiter check, or the grace check."""
    import importlib
    src = Path(watcher.__file__).read_text()
    cases = [
        ("waiter pidfile ignored",
         "    if _waiter_pid_alive(state_dir, persona):\n        return True\n",
         "", "test_waiter_pidfile_counts_as_alive"),
        ("re-arm grace ignored",
         "WAITER_REARM_GRACE_SEC = 120\n", "WAITER_REARM_GRACE_SEC = 0\n",
         "test_recent_offset_within_grace_counts_as_alive"),
    ]
    killed = 0
    for name, old, new, test in cases:
        assert src.count(old) == 1, f"MUTATION HARNESS BROKEN: {name}: pattern count {src.count(old)}"
        mod_src = src.replace(old, new, 1)
        assert mod_src != src
        mut = type(sys)("watcher_mut")
        mut.__dict__["__file__"] = watcher.__file__
        exec(compile(mod_src, "watcher_mut", "exec"), mut.__dict__)
        orig = sys.modules["watcher"]
        sys.modules["watcher"] = mut
        globals()["watcher"] = mut
        try:
            r = unittest.TextTestRunner(stream=open(os.devnull, "w")).run(
                unittest.TestSuite([WaiterLivenessTest(test)]))
        finally:
            sys.modules["watcher"] = orig
            globals()["watcher"] = orig
        if r.failures or r.errors:
            print(f"KILLED: {name} — {test} detects this")
            killed += 1
        else:
            print(f"SURVIVED: {name}")
    return killed == len(cases)


if __name__ == "__main__":
    prog = unittest.main(exit=False)
    ok = prog.result.wasSuccessful() and _mutation_checks()
    sys.exit(0 if ok else 1)

"""Tests for in-loop channel re-discovery (inter#211).

The watcher used to discover channels once at startup, so a channel created
later was never watched until a restart. These tests run against temp dirs and
never touch the real sessionbridge state.

Run with:
    python3 federation-watcher/test_discovery.py -v
"""

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

WATCHER_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(WATCHER_DIR))

import watcher  # noqa: E402


def write_channel(chdir: Path, name: str, msgs: list[dict]) -> None:
    with open(chdir / f"{name}.jsonl", "w") as f:
        for m in msgs:
            f.write(json.dumps(m) + "\n")


class RefreshChannelsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.chdir = root / "channels"
        self.state = root / "state"
        self.chdir.mkdir()
        self.state.mkdir()
        self._orig = watcher.SESSIONBRIDGE_CHANNELS
        watcher.SESSIONBRIDGE_CHANNELS = self.chdir
        self.start = datetime(2026, 10, 24, 12, 0, tzinfo=timezone.utc)

    def tearDown(self):
        watcher.SESSIONBRIDGE_CHANNELS = self._orig
        self.tmp.cleanup()

    def ts(self, minutes: int) -> str:
        return (self.start + timedelta(minutes=minutes)).isoformat()

    def test_new_channel_is_added_and_post_start_messages_are_delivered(self):
        write_channel(self.chdir, "live-test", [{"seq": 1, "ts": self.ts(-60)}])
        channels = ["live-test"]
        # a channel created after the watcher started, whose first message is an @mention
        write_channel(self.chdir, "mdcu-spike", [
            {"seq": 1, "ts": self.ts(5), "text": "@deming box-safety?"},
            {"seq": 2, "ts": self.ts(6)},
        ])
        added = watcher.refresh_channels(channels, self.state, self.start)
        self.assertEqual(added, ["mdcu-spike"])
        self.assertIn("mdcu-spike", channels)
        # last_seq = 0, so seq 1 (the first @mention) is still delivered
        self.assertEqual(watcher.get_last_seq(self.state, "mdcu-spike"), 0)
        new = watcher.read_new_messages("mdcu-spike", 0)
        self.assertEqual([m["seq"] for m in new], [1, 2])

    def test_pre_start_history_is_not_replayed(self):
        channels: list[str] = []
        write_channel(self.chdir, "old-chan", [
            {"seq": 1, "ts": self.ts(-30)},
            {"seq": 2, "ts": self.ts(-10)},
            {"seq": 3, "ts": self.ts(2)},
        ])
        watcher.refresh_channels(channels, self.state, self.start)
        # only seq 3 (posted after start) is pending
        self.assertEqual(watcher.get_last_seq(self.state, "old-chan"), 2)

    def test_existing_state_is_kept(self):
        write_channel(self.chdir, "chan", [{"seq": 9, "ts": self.ts(1)}])
        watcher.set_last_seq(self.state, "chan", 7)
        channels: list[str] = []
        watcher.refresh_channels(channels, self.state, self.start)
        self.assertEqual(watcher.get_last_seq(self.state, "chan"), 7)

    def test_no_new_channel_adds_nothing(self):
        write_channel(self.chdir, "live-test", [{"seq": 1, "ts": self.ts(0)}])
        channels = ["live-test"]
        self.assertEqual(watcher.refresh_channels(channels, self.state, self.start), [])
        self.assertEqual(channels, ["live-test"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import unittest

from agent_control.events import safe_event


class SafeEventTests(unittest.TestCase):
    def test_redacts_hidden_and_secret_fields(self) -> None:
        event = safe_event(
            "tool.completed",
            {"status": "completed", "summary": "done", "password": "hidden", "reasoning": "hidden"},
            {"run_id": "run-1"},
            1,
        )
        self.assertEqual(event.payload, {"status": "completed", "summary": "done"})

    def test_rejects_unknown_event(self) -> None:
        with self.assertRaises(ValueError):
            safe_event("unknown", {}, {"run_id": "run-1"}, 1)


if __name__ == "__main__":
    unittest.main()

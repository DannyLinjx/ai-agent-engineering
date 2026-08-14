from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "templates/browser-react-fastapi/backend"
SCRIPTS = ROOT / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from agent_control.events import safe_event
import create_agent_from_blueprint as factory


class BrowserOverlayTests(unittest.TestCase):
    def test_safe_event_redacts_untrusted_payload_and_bounds_output(self) -> None:
        event = safe_event(
            "tool.completed",
            {
                "tool": "search",
                "output_preview": "x" * 5000,
                "nested": {"api_key": "sk-test-secret", "safe": "visible"},
                "absolute_path": "/Users/alice/private.txt",
                "reasoning": "hidden chain of thought",
                "items": list(range(100)),
                "status": "completed",
            },
            {"run_id": "run-1"},
            2,
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

        self.assertEqual(event.id, "run-1:2")
        self.assertEqual(event.status, "completed")
        self.assertEqual(event.payload["nested"], {"safe": "visible"})
        self.assertNotIn("absolute_path", event.payload)
        self.assertNotIn("reasoning", event.payload)
        self.assertLessEqual(len(event.payload["output_preview"]), 1000)
        self.assertLessEqual(len(event.payload["items"]), 50)

    def test_safe_event_rejects_unknown_type(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported browser event"):
            safe_event("model.hidden_reasoning", {}, {"run_id": "run-1"}, 1)

    def test_browser_profile_generates_overlay_without_installing_or_starting(self) -> None:
        blueprint = json.loads((ROOT / "examples/local-memory-agent-blueprint.json").read_text(encoding="utf-8"))
        recipe = factory.build_recipe(blueprint)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "browser-agent"
            factory.apply_blueprint(blueprint, recipe, target)

            self.assertTrue((target / "src/agent_control/events.py").is_file())
            self.assertTrue((target / "tests/test_browser_events.py").is_file())
            self.assertTrue((target / "web/index.html").is_file())
            self.assertTrue((target / "web/package.json").is_file())
            for forbidden in ("web/node_modules", ".venv", ".env", "browser.pid"):
                self.assertFalse((target / forbidden).exists(), forbidden)


if __name__ == "__main__":
    unittest.main()

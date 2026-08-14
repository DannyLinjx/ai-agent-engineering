from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import create_agent_from_blueprint as factory


class FactoryProfileTests(unittest.TestCase):
    def test_legacy_blueprint_normalizes_to_safe_profiles(self) -> None:
        blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))

        normalized = factory.normalize_profiles(blueprint)

        self.assertEqual(
            normalized["experience"],
            {
                "profile": "headless",
                "reference_stack": "none",
                "auth": "none",
                "realtime": "none",
                "surfaces": [],
            },
        )
        self.assertEqual(
            normalized["memory"],
            {
                "enabled": False,
                "profile": "local",
                "canonical_store": "sqlite",
                "keyword_index": "sqlite_fts5",
                "vector_index": "none",
                "graph_store": "none",
                "framework": "native",
            },
        )
        self.assertEqual(normalized["delivery"], {"engagement": "plan_only"})
        self.assertNotIn("experience", blueprint)
        self.assertNotIn("memory", blueprint)
        self.assertNotIn("delivery", blueprint)


if __name__ == "__main__":
    unittest.main()

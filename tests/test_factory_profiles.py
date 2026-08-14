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
    def blueprint(self) -> dict:
        return json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))

    def test_legacy_blueprint_normalizes_to_safe_profiles(self) -> None:
        blueprint = self.blueprint()

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

    def test_invalid_profile_combinations_are_blocked(self) -> None:
        cases = [
            (
                {
                    "experience": {
                        "profile": "operations_console",
                        "reference_stack": "react_fastapi",
                        "auth": "none",
                        "realtime": "sse",
                        "surfaces": ["overview"],
                    }
                },
                "experience-auth-required",
            ),
            (
                {
                    "experience": {
                        "profile": "browser_chat",
                        "reference_stack": "none",
                        "auth": "server_session",
                        "realtime": "sse",
                        "surfaces": ["conversation"],
                    }
                },
                "experience-stack-required",
            ),
            (
                {
                    "memory": {
                        "enabled": True,
                        "profile": "enterprise",
                        "canonical_store": "sqlite",
                        "keyword_index": "sqlite_fts5",
                        "vector_index": "none",
                        "graph_store": "none",
                        "framework": "native",
                    }
                },
                "enterprise-canonical-store",
            ),
        ]

        for update, expected_code in cases:
            with self.subTest(expected_code=expected_code):
                blueprint = self.blueprint()
                blueprint.update(update)
                recipe = factory.build_recipe(blueprint)
                self.assertEqual(recipe["status"], "blocked")
                self.assertIn(expected_code, {item["code"] for item in recipe["blockers"]})

    def test_profiles_derive_required_capabilities(self) -> None:
        blueprint = self.blueprint()
        blueprint["experience"] = {
            "profile": "operations_console",
            "reference_stack": "react_fastapi",
            "auth": "server_session",
            "realtime": "sse",
            "surfaces": ["conversation", "run_inspector", "overview", "memory"],
        }
        blueprint["memory"] = {
            "enabled": True,
            "profile": "enterprise",
            "canonical_store": "postgresql",
            "keyword_index": "postgres_fts",
            "vector_index": "pgvector",
            "graph_store": "none",
            "framework": "native",
        }

        recipe = factory.build_recipe(blueprint)

        self.assertEqual(recipe["status"], "planned")
        self.assertTrue(
            {
                "browser-experience",
                "session",
                "checkpoint",
                "security",
                "permissions",
                "verification",
                "observability",
                "operations",
                "multi-user-isolation",
                "audit-and-artifacts",
                "realtime-events",
                "memory",
                "memory-governance",
                "memory-migration",
                "backup-and-recovery",
            }.issubset(set(recipe["derived_required"]))
        )
        self.assertTrue({"P0", "P3", "P5", "P8", "P10"}.issubset(set(recipe["applicable_phases"])))


if __name__ == "__main__":
    unittest.main()

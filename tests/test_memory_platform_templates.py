from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import plan_memory_deployment as planner


class MemoryPlatformTemplateTests(unittest.TestCase):
    def request(self, **overrides) -> dict:
        value = {
            "profile": "local",
            "users": 1,
            "tenant_count": 1,
            "expected_records": 10000,
            "concurrent_writers": 1,
            "latency_target_ms": 500,
            "availability_target": 0.99,
            "semantic_retrieval_required": False,
            "graph_queries": [],
            "graph_acceptance_cases": [],
            "managed_preference": "self_hosted",
            "data_class": "internal",
            "engagement": "plan_only",
        }
        value.update(overrides)
        return value

    def test_planner_selects_minimal_topology(self) -> None:
        local = planner.build_deployment_plan(self.request())
        hybrid = planner.build_deployment_plan(
            self.request(
                profile="hybrid",
                users=100,
                tenant_count=5,
                expected_records=1_000_000,
                concurrent_writers=20,
                semantic_retrieval_required=True,
                engagement="guided_install",
            )
        )

        self.assertEqual(local["topology"]["canonical_store"], "sqlite")
        self.assertEqual(local["topology"]["keyword_index"], "sqlite_fts5")
        self.assertEqual(local["services"], [])
        self.assertEqual(hybrid["topology"]["canonical_store"], "postgresql")
        self.assertEqual(hybrid["topology"]["vector_index"], "pgvector")
        self.assertNotIn("redis", hybrid["topology"].values())
        for plan in (local, hybrid):
            self.assertFalse(plan["installation_allowed"])
            self.assertFalse(plan["deployment_allowed"])

    def test_graph_store_requires_acceptance_case(self) -> None:
        with self.assertRaisesRegex(ValueError, "graph acceptance"):
            planner.build_deployment_plan(
                self.request(
                    profile="enterprise",
                    graph_queries=["relationship traversal"],
                    graph_acceptance_cases=[],
                )
            )

    def test_cli_writes_only_the_named_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            request_path = root / "request.json"
            output_path = root / "plan.json"
            request_path.write_text(json.dumps(self.request()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "plan_memory_deployment.py"),
                    "--request",
                    str(request_path),
                    "--output",
                    str(output_path),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout)
            self.assertEqual({path.name for path in root.iterdir()}, {"request.json", "plan.json"})
            self.assertFalse((root / ".env").exists())
            self.assertFalse((root / "compose.yaml").exists())


if __name__ == "__main__":
    unittest.main()

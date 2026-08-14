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

import create_agent_from_blueprint as factory
import scaffold_agent_project as scaffolder


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
        self.assertEqual(recipe["overlays"], ["browser-react-fastapi"])
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

    def test_apply_emits_profile_manifests_without_install_authority(self) -> None:
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
        blueprint["delivery"] = {"engagement": "end_to_end"}
        recipe = factory.build_recipe(blueprint)

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "profiled-agent"
            report = factory.apply_blueprint(blueprint, recipe, target)

            for name in ("experience-manifest.json", "memory-manifest.json", "deployment-plan.json"):
                self.assertTrue((target / "factory" / name).is_file(), name)
            self.assertTrue((target / "docs/browser-experience.md").is_file())
            deployment = json.loads((target / "factory/deployment-plan.json").read_text(encoding="utf-8"))
            self.assertFalse(deployment["installation_allowed"])
            self.assertFalse(deployment["deployment_allowed"])
            self.assertEqual(deployment["engagement"], "end_to_end")
            self.assertEqual(report["status"], "awaiting_human_approval")
            self.assertTrue(
                {"factory/experience-manifest.json", "factory/memory-manifest.json", "factory/deployment-plan.json"}.issubset(
                    set(report["artifacts"])
                )
            )

    def test_profile_plan_is_byte_deterministic(self) -> None:
        blueprint = self.blueprint()
        blueprint["experience"] = {
            "profile": "browser_chat",
            "reference_stack": "react_fastapi",
            "auth": "local_account",
            "realtime": "sse",
            "surfaces": ["conversation", "run_inspector"],
        }

        first = factory.canonical_bytes(factory.build_recipe(blueprint))
        second = factory.canonical_bytes(factory.build_recipe(blueprint))

        self.assertEqual(first, second)

    def test_manifest_validators_accept_generated_and_reject_conflict(self) -> None:
        blueprint = self.blueprint()
        blueprint["experience"] = {
            "profile": "browser_chat",
            "reference_stack": "react_fastapi",
            "auth": "server_session",
            "realtime": "sse",
            "surfaces": ["conversation", "run_inspector"],
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

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "validated-agent"
            factory.apply_blueprint(blueprint, recipe, target)
            experience = target / "factory/experience-manifest.json"
            memory = target / "factory/memory-manifest.json"
            python = sys.executable
            accepted_experience = subprocess.run(
                [python, str(SCRIPTS / "validate_experience_manifest.py"), "--manifest", str(experience), "--json"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            accepted_memory = subprocess.run(
                [python, str(SCRIPTS / "validate_memory_manifest.py"), "--manifest", str(memory), "--json"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(accepted_experience.returncode, 0, accepted_experience.stdout)
            self.assertEqual(accepted_memory.returncode, 0, accepted_memory.stdout)

            broken = json.loads(memory.read_text(encoding="utf-8"))
            broken["canonical_store"] = "sqlite"
            memory.write_text(json.dumps(broken), encoding="utf-8")
            rejected = subprocess.run(
                [python, str(SCRIPTS / "validate_memory_manifest.py"), "--manifest", str(memory), "--json"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(rejected.returncode, 1, rejected.stdout)
            self.assertIn("enterprise-canonical-store", rejected.stdout)

    def test_scaffold_composes_overlay_without_mutating_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "browser-agent"

            generated = scaffolder.scaffold_project(
                "python",
                "Browser Agent",
                target,
                dry_run=True,
                overlays=("browser-react-fastapi",),
            )

            self.assertIn("docs/browser-experience.md", generated)
            self.assertFalse(target.exists())

    def test_scaffold_rejects_conflicting_overlay_destinations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_root = Path(tmp) / "skill"
            templates = skill_root / "templates"
            (templates / "python-agent").mkdir(parents=True)
            (templates / "python-agent/base.txt").write_text("base", encoding="utf-8")
            for name, content in (("overlay-a", "first"), ("overlay-b", "second")):
                overlay = templates / name
                overlay.mkdir()
                (overlay / "payload.txt").write_text(content, encoding="utf-8")
                (overlay / "overlay-manifest.json").write_text(
                    json.dumps(
                        {
                            "version": "1.0",
                            "files": [
                                {"source": "payload.txt", "destination": "docs/conflict.txt"},
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
            original_root = scaffolder.SKILL_ROOT
            scaffolder.SKILL_ROOT = skill_root
            try:
                with self.assertRaisesRegex(ValueError, "conflicting overlay destination"):
                    scaffolder.scaffold_project(
                        "python",
                        "Conflict Agent",
                        Path(tmp) / "target",
                        dry_run=True,
                        overlays=("overlay-a", "overlay-b"),
                    )
            finally:
                scaffolder.SKILL_ROOT = original_root


if __name__ == "__main__":
    unittest.main()

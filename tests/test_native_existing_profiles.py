"""Planning supports existing native/file runtimes without inventing generators."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import create_agent_from_blueprint as factory
import plan_memory_deployment as planner
import validate_experience_manifest as experiences
import validate_memory_manifest as memories


class NativeExistingProfileTests(unittest.TestCase):
    def blueprint(self):
        value = json.loads((ROOT / "templates/agent-blueprint.json").read_text())
        value["experience"] = {"profile": "native_chat", "reference_stack": "native_cli",
                               "auth": "local_account", "realtime": "stdio", "surfaces": []}
        return value

    def test_native_apply_plans_surfaces_without_web_dependencies(self):
        value = self.blueprint()
        recipe = factory.build_recipe(value)
        self.assertEqual(recipe["status"], "planned", recipe["blockers"])
        self.assertEqual(recipe["overlays"], [])
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "candidate"
            factory.apply_blueprint(value, recipe, target)
            manifest = json.loads((target / "factory/experience-manifest.json").read_text())
            deployment = json.loads((target / "factory/deployment-plan.json").read_text())
            self.assertEqual(manifest["status"], "planned")
            self.assertEqual(manifest["generated_surfaces"], [])
            self.assertIn("conversation", manifest["planned_surfaces"])
            self.assertEqual(experiences.validate_manifest(manifest), [])
            self.assertFalse((target / "web").exists())
            self.assertFalse((target / "backend").exists())
            self.assertNotIn("react-vite-build", deployment["dependencies"])
            self.assertNotIn("python-fastapi-control-plane", deployment["dependencies"])

    def test_native_transport_and_stack_do_not_silently_mix_with_web(self):
        for field, value in [("reference_stack", "react_fastapi"), ("realtime", "sse"),
                             ("auth", "none")]:
            blueprint = self.blueprint()
            blueprint["experience"][field] = value
            with self.subTest(field=field):
                self.assertEqual(factory.build_recipe(blueprint)["status"], "blocked")
        blueprint = self.blueprint()
        blueprint["experience"]["realtime"] = "local_ipc"
        self.assertEqual(factory.build_recipe(blueprint)["status"], "planned")

    def test_manifest_cannot_claim_unimplemented_native_generator(self):
        value = self.blueprint()
        manifest = factory._experience_manifest(value, factory.build_recipe(value))
        manifest.update(status="generated", generated_surfaces=["conversation"])
        self.assertIn("native-generator-unavailable", {x["code"] for x in experiences.validate_manifest(manifest)})

    def test_file_memory_manifests_preserve_planned_authority(self):
        for store in ("encrypted_files", "scoped_markdown"):
            value = self.blueprint()
            value["memory"] = {"enabled": True, "profile": "local", "canonical_store": store,
                               "keyword_index": "none", "vector_index": "none",
                               "graph_store": "none", "framework": "native"}
            recipe = factory.build_recipe(value)
            self.assertEqual(recipe["status"], "planned", recipe["blockers"])
            with tempfile.TemporaryDirectory() as temporary:
                target = Path(temporary) / "candidate"
                factory.apply_blueprint(value, recipe, target)
                manifest = json.loads((target / "factory/memory-manifest.json").read_text())
                self.assertEqual(manifest["canonical_store"], store)
                self.assertEqual(manifest["status"], "planned")
                self.assertEqual(memories.validate_manifest(manifest), [])
                deployment = json.loads((target / "factory/deployment-plan.json").read_text())
                self.assertFalse({"sqlite", "postgresql"} & set(deployment["dependencies"]))
                config = json.loads((target / "config/memory.config.json").read_text())
                self.assertEqual(config["canonical_store"], store)
                self.assertFalse(config["enabled"])
                self.assertIsNone(config["connection"]["database_url"])

    def test_file_memory_does_not_inherit_database_specific_index(self):
        value = self.blueprint()
        value["memory"] = {"enabled": True, "canonical_store": "encrypted_files"}
        normalized = factory.normalize_profiles(value)
        self.assertEqual(normalized["memory"]["keyword_index"], "none")
        self.assertEqual(factory.build_recipe(value)["status"], "planned")

    def test_zero_step_count_is_valid_planning_with_positive_other_budgets(self):
        value = self.blueprint()
        value["service"]["max_steps"] = 0
        self.assertEqual(factory.build_recipe(value)["status"], "planned")
        value["service"]["deadline_seconds"] = 0
        self.assertEqual(factory.build_recipe(value)["status"], "blocked")

    def test_zero_step_scaffold_is_rejected_before_any_target_write(self):
        value = self.blueprint()
        value["service"]["max_steps"] = 0
        recipe = factory.build_recipe(value)
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "candidate"
            with self.assertRaisesRegex(ValueError, "governed-runtime-required"):
                factory.apply_blueprint(value, recipe, target)
            self.assertFalse(target.exists())

    def test_existing_file_topology_is_not_migrated_by_memory_planner(self):
        request = json.loads((ROOT / "examples/memory-deployment-request.json").read_text())
        request.update(profile="local", existing_canonical_store="encrypted_files",
                       semantic_retrieval_required=False, graph_queries=[], graph_acceptance_cases=[])
        plan = planner.build_deployment_plan(request)
        self.assertEqual(plan["topology"]["canonical_store"], "encrypted_files")
        self.assertEqual(plan["services"], [])
        self.assertFalse(plan["migration"]["required"])
        self.assertFalse(plan["installation_allowed"])

    def test_json_contracts_accept_native_and_existing_file_profiles(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("Optional jsonschema is absent; manifest validators still run in other cases")
        blueprint = self.blueprint()
        blueprint["service"]["max_steps"] = 0
        blueprint["memory"] = {"enabled": True, "canonical_store": "encrypted_files"}
        schema = json.loads((ROOT / "schemas/agent-blueprint.schema.json").read_text())
        jsonschema.validate(blueprint, schema)
        recipe = factory.build_recipe(blueprint)
        for name, data in [("experience", factory._experience_manifest(blueprint, recipe)),
                           ("memory", factory._memory_manifest(blueprint, recipe))]:
            schema = json.loads((ROOT / f"schemas/{name}-manifest.schema.json").read_text())
            jsonschema.validate(data, schema)


if __name__ == "__main__":
    unittest.main()

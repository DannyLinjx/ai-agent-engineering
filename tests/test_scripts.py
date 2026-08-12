from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

def run_script(name: str, *args: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run([sys.executable, str(SCRIPTS / name), *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    if completed.returncode != expected:
        raise AssertionError(f"{name} returned {completed.returncode}, expected {expected}\n{completed.stdout}")
    return completed

class SkillScriptTests(unittest.TestCase):
    def test_all_json_files_parse(self) -> None:
        for path in ROOT.rglob("*.json"):
            with self.subTest(path=path): json.loads(path.read_text(encoding="utf-8"))
        for path in ROOT.rglob("*.jsonl"):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip(): json.loads(line)

    def test_agent_blueprint_contract_and_examples(self) -> None:
        schema_path = ROOT / "schemas/agent-blueprint.schema.json"
        template_path = ROOT / "templates/agent-blueprint.json"
        example_path = ROOT / "examples/enterprise-agent-blueprint.json"
        self.assertTrue(schema_path.is_file())
        self.assertTrue(template_path.is_file())
        self.assertTrue(example_path.is_file())
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        required = set(schema["required"])
        expected = {
            "version", "blueprint_id", "agent", "product", "perception", "data_governance",
            "capabilities", "autonomy", "service", "implementation", "verification", "assumptions", "unknowns",
        }
        self.assertEqual(required, expected)
        for path in (template_path, example_path):
            value = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(expected.issubset(value))
            serialized = json.dumps(value, ensure_ascii=False).lower()
            for credential in ("api_key", "password", "secret", "token"):
                self.assertNotIn(f'"{credential}"', serialized)
        template = json.loads(template_path.read_text(encoding="utf-8"))
        self.assertEqual(template["implementation"]["profile"], "development")
        self.assertEqual(template["implementation"]["optional_integrations"], {"channels": "none", "model_provider": "mock", "mcp": "none"})
        example = json.loads(example_path.read_text(encoding="utf-8"))
        self.assertTrue(example["perception"]["modalities"])
        self.assertTrue(example["capabilities"]["required"])
        self.assertTrue(example["autonomy"]["approval_required_actions"])
        self.assertTrue(example["product"]["acceptance_criteria"])
        self.assertTrue(example["verification"]["deterministic_assertions"])

    def test_agent_factory_plan_is_deterministic_and_non_mutating(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "enterprise-agent"
            first = root / "recipe-first.json"
            second = root / "recipe-second.json"
            args = ("--blueprint", str(ROOT / "examples/enterprise-agent-blueprint.json"), "--target", str(target))
            run_script("create_agent_from_blueprint.py", *args, "--plan", str(first))
            run_script("create_agent_from_blueprint.py", *args, "--plan", str(second))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            recipe = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(recipe["status"], "planned")
            self.assertFalse(target.exists())
            self.assertIn("production_release", recipe["human_approvals"])
            self.assertEqual(len(recipe["recipe_hash"]), 64)
            classified = set(recipe["capabilities"]["selected"]) | set(recipe["capabilities"]["planned"]) | set(recipe["capabilities"]["blocked"])
            blueprint = json.loads((ROOT / "examples/enterprise-agent-blueprint.json").read_text(encoding="utf-8"))
            self.assertTrue(set(blueprint["capabilities"]["required"]).issubset(classified))

    def test_agent_factory_plan_rejects_output_inside_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "planned-agent"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(ROOT / "templates/agent-blueprint.json"),
                "--target", str(target), "--plan", str(target / "build-recipe.json"),
                expected=2,
            )
            self.assertFalse(target.exists())

    def test_agent_factory_blocks_material_unknown_without_target_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "blocked-blueprint.json"
            value = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            value["unknowns"].append({"id": "u1", "statement": "Production data authority is unresolved", "risk": "high", "resolution": "open"})
            blueprint_path.write_text(json.dumps(value), encoding="utf-8")
            target = root / "blocked-agent"
            recipe_path = root / "blocked-recipe.json"
            run_script("create_agent_from_blueprint.py", "--blueprint", str(blueprint_path), "--target", str(target), "--plan", str(recipe_path), expected=1)
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertEqual(recipe["status"], "blocked")
            self.assertTrue(any(item["code"] == "material-unknown" for item in recipe["blockers"]))
            self.assertFalse(target.exists())

    def test_agent_factory_apply_generates_candidate_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "enterprise-agent"
            report_path = root / "creation-report.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(ROOT / "examples/enterprise-agent-blueprint.json"),
                "--target", str(target), "--apply", "--report", str(report_path),
            )
            self.assertTrue((target / "src/agent_runtime/runtime.py").is_file())
            for name in ("agent-blueprint.json", "build-recipe.json", "capability-matrix.json", "assembly-manifest.json", "release-checklist.json"):
                self.assertTrue((target / "factory" / name).is_file(), name)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "awaiting_human_approval")
            self.assertNotIn("deploy", json.dumps(report).lower())
            integrations = json.loads((target / "config/integrations.config.json").read_text(encoding="utf-8"))
            blueprint = json.loads((ROOT / "examples/enterprise-agent-blueprint.json").read_text(encoding="utf-8"))
            expected_integrations = blueprint["implementation"]["optional_integrations"]
            self.assertEqual(integrations["profile"], blueprint["implementation"]["profile"])
            self.assertEqual(integrations["channels"]["selection"], expected_integrations["channels"])
            self.assertEqual(integrations["model_providers"]["selection"], expected_integrations["model_provider"])
            self.assertEqual(integrations["mcp"]["selection"], expected_integrations["mcp"])
            matrix = json.loads((target / "factory/capability-matrix.json").read_text(encoding="utf-8"))
            required = set(blueprint["capabilities"]["required"])
            records = {item["capability"]: item for item in matrix["capabilities"]}
            self.assertTrue(required.issubset(records))
            self.assertTrue(all(records[name]["status"] in {"implemented", "planned", "blocked"} for name in required))
            self.assertTrue(all(records[name]["evidence"] for name in required if records[name]["status"] == "implemented"))

    def test_agent_factory_apply_supports_generic_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "generic-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["implementation"]["language"] = "generic"
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            target = root / "generic-agent"
            run_script("create_agent_from_blueprint.py", "--blueprint", str(blueprint_path), "--target", str(target), "--apply")
            self.assertTrue((target / "architecture/module-plan.md").is_file())
            self.assertTrue((target / "schemas/agent-state.schema.json").is_file())
            self.assertTrue((target / "factory/build-recipe.json").is_file())
            self.assertFalse((target / "src").exists())

    def test_agent_factory_rejects_non_empty_target_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing-agent"
            target.mkdir()
            sentinel = target / "sentinel.txt"
            sentinel.write_text("preserve-me", encoding="utf-8")
            before = sorted(path.name for path in target.iterdir())
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(ROOT / "templates/agent-blueprint.json"),
                "--target", str(target), "--apply", expected=2,
            )
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve-me")
            self.assertEqual(sorted(path.name for path in target.iterdir()), before)

    def test_agent_factory_rejects_inline_credentials_before_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "credential-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["api_key"] = "raw-secret-value"
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            target = root / "credential-agent"
            recipe_path = root / "credential-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(target),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertTrue(any(item["code"] == "inline-credential" for item in recipe["blockers"]))
            self.assertFalse(target.exists())

    def test_agent_factory_requires_approval_for_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "external-write-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["autonomy"]["allowed_actions"].append("write customer reply to external system")
            blueprint["autonomy"]["approval_required_actions"].remove("external_write")
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            recipe_path = root / "external-write-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(root / "external-write-agent"),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertTrue(any(item["code"] == "approval-required" for item in recipe["blockers"]))

    def test_agent_factory_requires_approval_for_chinese_external_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "chinese-external-write-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["autonomy"]["allowed_actions"].append("向外部系统写入客户回复")
            blueprint["autonomy"]["approval_required_actions"].remove("external_write")
            blueprint_path.write_text(json.dumps(blueprint, ensure_ascii=False), encoding="utf-8")
            recipe_path = root / "chinese-external-write-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(root / "chinese-external-write-agent"),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertTrue(any(item["code"] == "approval-required" for item in recipe["blockers"]))

    def test_agent_factory_rejects_invalid_contract_values(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "invalid-contract-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["agent"]["owner"] = ""
            blueprint["product"]["objective"] = ""
            blueprint["perception"]["modalities"] = ["audio"]
            blueprint["data_governance"]["data_classes"] = ["secret"]
            blueprint["data_governance"]["tenant_isolation"] = "yes"
            blueprint["data_governance"]["retention_days"] = -1
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            target = root / "invalid-contract-agent"
            recipe_path = root / "invalid-contract-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(target),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            paths = {item.get("path") for item in recipe["blockers"]}
            self.assertTrue({
                "agent.owner", "product.objective", "perception.modalities[0]",
                "data_governance.data_classes[0]", "data_governance.tenant_isolation",
                "data_governance.retention_days",
            }.issubset(paths))
            self.assertFalse(target.exists())

    def test_agent_factory_malformed_section_returns_blocked_recipe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "malformed-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["capabilities"] = []
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            target = root / "malformed-agent"
            recipe_path = root / "malformed-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(target),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertEqual(recipe["status"], "blocked")
            self.assertTrue(any(item["path"] == "capabilities" for item in recipe["blockers"]))
            self.assertFalse(target.exists())

    def test_agent_factory_required_capability_must_be_catalogued(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blueprint_path = root / "unknown-capability-blueprint.json"
            blueprint = json.loads((ROOT / "templates/agent-blueprint.json").read_text(encoding="utf-8"))
            blueprint["capabilities"]["required"].append("unregistered-enterprise-system")
            blueprint_path.write_text(json.dumps(blueprint), encoding="utf-8")
            recipe_path = root / "unknown-capability-recipe.json"
            run_script(
                "create_agent_from_blueprint.py",
                "--blueprint", str(blueprint_path), "--target", str(root / "unknown-capability-agent"),
                "--plan", str(recipe_path), expected=1,
            )
            recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
            self.assertTrue(any(item["code"] == "unknown-capability" for item in recipe["blockers"]))

    def test_structure_validator(self) -> None:
        output = run_script("validate_skill_structure.py", "--skill", str(ROOT), "--json").stdout
        self.assertEqual(json.loads(output)["status"], "passed")

    def test_agent_factory_is_routed_and_gated(self) -> None:
        required_resources = {
            "references/agent-factory.md", "schemas/agent-blueprint.schema.json", "templates/agent-blueprint.json",
            "assets/agent-factory-flow.mmd", "scripts/create_agent_from_blueprint.py", "examples/enterprise-agent-blueprint.json",
        }
        for rel in required_resources:
            self.assertTrue((ROOT / rel).is_file(), rel)
        validator = (ROOT / "scripts/validate_skill_structure.py").read_text(encoding="utf-8")
        self.assertTrue(all(f'"{rel}"' in validator for rel in required_resources))
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/agent-factory.md", skill)
        self.assertIn("create_agent_from_blueprint.py", skill)
        self.assertIn("--plan", skill)
        self.assertIn("--apply", skill)
        catalog = json.loads((ROOT / "assets/capability-catalog.json").read_text(encoding="utf-8"))
        self.assertIn("agent-factory", catalog["capabilities"])
        self.assertIn("perception-input", catalog["capabilities"])
        phases = (ROOT / "assets/phase-gates.yaml").read_text(encoding="utf-8")
        self.assertIn("agent-blueprint", phases)
        self.assertIn("build-recipe", phases)
        self.assertIn("factory-evidence-bundle", phases)
        self.assertIn("human-release-approval", phases)
        evals = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
        factory_case = next(case for case in evals["cases"] if case["id"] == "create-enterprise-agent-factory")
        expected = set(factory_case["expected"])
        self.assertTrue({"agent blueprint", "build recipe", "candidate evidence", "human release approval"}.issubset(expected))

    def test_structure_validator_treats_host_metadata_as_optional(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "ai-agent-engineering"
            shutil.copytree(ROOT, skill, ignore=shutil.ignore_patterns(".git", ".DS_Store", "__pycache__"))
            (skill / "agents/openai.yaml").unlink()
            output = json.loads(run_script("validate_skill_structure.py", "--skill", str(skill), "--json").stdout)
            self.assertEqual(output["core_status"], "passed")
            self.assertEqual(output["optional_host_adapters"]["agents/openai.yaml"], "missing")
            self.assertTrue(any(item["code"] == "optional-host-adapter" for item in output["warnings"]))

    def test_python_scaffold_and_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo-agent"
            run_script("scaffold_agent_project.py", "--language", "python", "--name", "Demo Agent", "--target", str(project))
            self.assertTrue((project / "src/agent_runtime/runtime.py").is_file())
            self.assertTrue((project / "config/integrations.config.json").is_file())
            self.assertTrue((project / "config/agent-instructions.md").is_file())
            self.assertTrue((project / "config/tool-manifest.json").is_file())
            self.assertTrue((project / "skills").is_dir())
            self.assertTrue((project / "data").is_dir())
            self.assertTrue((project / ".artifacts").is_dir())
            integration = json.loads(run_script("validate_integration_config.py", "--config", str(project / "config/integrations.config.json"), "--profile", "development", "--json").stdout)
            self.assertEqual(integration["details"]["selections"], {"channels": "none", "model_providers": "mock", "mcp": "none"})
            architecture = json.loads(run_script("validate_agent_architecture.py", "--project", str(project), "--json").stdout)
            self.assertEqual(architecture["status"], "passed")
            safety = json.loads(run_script("audit_agent_safety.py", "--project", str(project), "--json").stdout)
            self.assertEqual(safety["status"], "passed")
            manifest_path = Path(tmp) / "manifest.json"
            run_script("generate_module_manifest.py", "--project", str(project), "--output", str(manifest_path), "--include-hashes")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["language"], "python")
            report_path = Path(tmp) / "report.json"
            run_script("run_agent_acceptance_tests.py", "--project", str(project), "--config", str(ROOT / "examples/acceptance-commands-python.json"), "--report", str(report_path))
            self.assertEqual(json.loads(report_path.read_text(encoding="utf-8"))["status"], "passed")
            optional_report = Path(tmp) / "optional-report.json"
            run_script("run_agent_acceptance_tests.py", "--project", str(project), "--config", str(ROOT / "examples/acceptance-commands-optional-integrations.json"), "--report", str(optional_report))
            optional_value = json.loads(optional_report.read_text(encoding="utf-8"))
            self.assertEqual(optional_value["status"], "passed")
            self.assertEqual(optional_value["summary"]["skipped"], 4)

    def test_typescript_scaffold_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "ts-agent"
            output = run_script("scaffold_agent_project.py", "--language", "typescript", "--name", "TS Agent", "--target", str(target), "--dry-run").stdout
            self.assertIn("src/runtime/agent-runtime.ts", output)
            self.assertIn("config/integrations.config.json", output)
            self.assertFalse(target.exists())

    def test_generic_scaffold_is_language_neutral(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "generic-agent"
            run_script("scaffold_agent_project.py", "--language", "generic", "--name", "Generic Agent", "--target", str(project))
            self.assertTrue((project / "architecture/module-plan.md").is_file())
            self.assertTrue((project / "tests/contract-test-plan.md").is_file())
            self.assertTrue((project / "schemas/agent-state.schema.json").is_file())
            self.assertFalse((project / "src").exists())

    def test_acceptance_runner_rejects_required_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = root / "commands.json"
            config.write_text(json.dumps({"commands": [{"id": "expected-failure", "argv": [sys.executable, "-c", "raise SystemExit(3)"], "required": True}]}), encoding="utf-8")
            completed = run_script("run_agent_acceptance_tests.py", "--project", str(root), "--config", str(config), expected=1)
            self.assertEqual(json.loads(completed.stdout)["status"], "failed")

    def test_optional_integration_configuration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            default_config = root / "default.json"
            run_script("configure_integrations.py", "--output", str(default_config))
            default_value = json.loads(run_script("validate_integration_config.py", "--config", str(default_config), "--profile", "development", "--json").stdout)
            self.assertEqual(default_value["status"], "passed")
            self.assertEqual(default_value["details"]["test_matrix"], {"core": "run", "mock_model": "run", "live_model": "skipped", "channels": "skipped", "mcp": "skipped"})
            run_script("validate_integration_config.py", "--config", str(default_config), "--profile", "production", "--json", expected=1)

            configured = root / "configured.json"
            run_script("configure_integrations.py", "--profile", "production", "--channel", "feishu", "--channel", "wecom", "--model-provider", "openai", "--mcp-server", "github=stdio", "--output", str(configured))
            configured_value = json.loads(run_script("validate_integration_config.py", "--config", str(configured), "--profile", "production", "--json").stdout)
            self.assertEqual(configured_value["status"], "passed")
            self.assertEqual(configured_value["details"]["enabled"], {"channels": 2, "live_model_providers": 1, "mcp_servers": 1})

    def test_inline_integration_secret_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "invalid.json"
            value = json.loads((ROOT / "templates/integrations.config.json").read_text(encoding="utf-8"))
            value["channels"] = {"selection": "configured", "default": "telegram-main", "adapters": [{"id": "telegram-main", "type": "telegram", "enabled": True, "required": False, "credential_refs": {}, "settings": {"bot_token": "raw-secret-value"}}]}
            config.write_text(json.dumps(value), encoding="utf-8")
            output = json.loads(run_script("validate_integration_config.py", "--config", str(config), "--json", expected=1).stdout)
            self.assertTrue(any(item["code"] == "inline-secret" for item in output["issues"]))

if __name__ == "__main__": unittest.main()

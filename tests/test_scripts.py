from __future__ import annotations

import json
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

    def test_structure_validator(self) -> None:
        output = run_script("validate_skill_structure.py", "--skill", str(ROOT), "--json").stdout
        self.assertEqual(json.loads(output)["status"], "passed")

    def test_python_scaffold_and_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "demo-agent"
            run_script("scaffold_agent_project.py", "--language", "python", "--name", "Demo Agent", "--target", str(project))
            self.assertTrue((project / "src/agent_runtime/runtime.py").is_file())
            self.assertTrue((project / "config/integrations.config.json").is_file())
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

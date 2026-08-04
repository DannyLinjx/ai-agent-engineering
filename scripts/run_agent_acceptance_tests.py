#!/usr/bin/env python3
"""Run bounded acceptance commands and emit a machine-readable evidence report."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from _common import read_json, write_json

def safe_env(extra: dict[str, str] | None) -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key not in {"PYTHONINSPECT", "BASH_ENV", "ENV"}}
    for key, value in (extra or {}).items():
        if not isinstance(key, str) or not isinstance(value, str): raise ValueError("env values must be strings")
        env[key] = value
    return env

def run_case(case: dict, project: Path, max_output: int) -> dict:
    case_id = case.get("id")
    if case.get("enabled") is False:
        return {"id": str(case_id), "status": "skipped", "required": bool(case.get("required", False)), "reason": str(case.get("skip_reason", "optional integration is not configured"))}
    argv = case.get("argv")
    if not isinstance(case_id, str) or not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x for x in argv):
        return {"id": str(case_id), "status": "invalid", "required": bool(case.get("required", True)), "error": "id and non-empty string argv[] are required"}
    argv = [sys.executable if value == "{python}" else value for value in argv]
    timeout = int(case.get("timeout_seconds", 120))
    cwd = (project / case.get("cwd", ".")).resolve()
    try: cwd.relative_to(project)
    except ValueError: return {"id": case_id, "status": "invalid", "required": bool(case.get("required", True)), "error": "cwd escapes project"}
    start = time.monotonic()
    try:
        completed = subprocess.run(argv, cwd=cwd, env=safe_env(case.get("env")), text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=timeout, shell=False, check=False)
        output = completed.stdout or ""
        status = "passed" if completed.returncode == int(case.get("expected_exit_code", 0)) else "failed"
        return {"id": case_id, "status": status, "required": bool(case.get("required", True)), "argv": argv, "cwd": str(cwd), "exit_code": completed.returncode, "duration_seconds": round(time.monotonic() - start, 3), "output": output[-max_output:], "output_truncated": len(output) > max_output}
    except subprocess.TimeoutExpired as exc:
        output = (exc.stdout or "") if isinstance(exc.stdout, str) else ""
        return {"id": case_id, "status": "timeout", "required": bool(case.get("required", True)), "argv": argv, "cwd": str(cwd), "duration_seconds": round(time.monotonic() - start, 3), "output": output[-max_output:]}
    except OSError as exc:
        return {"id": case_id, "status": "error", "required": bool(case.get("required", True)), "argv": argv, "cwd": str(cwd), "duration_seconds": round(time.monotonic() - start, 3), "error": str(exc)}

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True, help="JSON with a commands array; argv must be an array, never a shell string")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--max-output-bytes", type=int, default=12000)
    args = parser.parse_args()
    project = args.project.expanduser().resolve()
    config = read_json(args.config.expanduser().resolve())
    commands = config.get("commands") if isinstance(config, dict) else None
    if not isinstance(commands, list) or not commands: parser.error("config must contain a non-empty commands array")
    started = datetime.now(timezone.utc).isoformat()
    results = [run_case(case, project, args.max_output_bytes) for case in commands]
    failed = [r for r in results if r.get("required", True) and r["status"] != "passed"]
    report = {"version": "1.0", "project": str(project), "started_at": started, "completed_at": datetime.now(timezone.utc).isoformat(), "status": "failed" if failed else "passed", "summary": {"total": len(results), "passed": sum(r["status"] == "passed" for r in results), "skipped": sum(r["status"] == "skipped" for r in results), "required_failed": len(failed)}, "cases": results}
    if args.report: write_json(args.report.expanduser().resolve(), report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if failed else 0

if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Run a conservative static audit for common agent safety control gaps."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from _common import emit, issue, iter_files, relative, result

PATTERNS = [
    ("shell-true", re.compile(r"shell\s*=\s*True"), "Subprocess uses shell parsing; prefer argument arrays"),
    ("unsafe-eval", re.compile(r"\b(eval|exec)\s*\("), "Dynamic evaluation requires a sandbox and explicit policy"),
    ("wildcard-cors", re.compile(r"allow_origins\s*=\s*\[?['\"]\*"), "Wildcard CORS may expose an agent API"),
    ("secret-literal", re.compile(r"(?i)(api[_-]?key|password|secret|token)\s*=\s*['\"][^'{][^'\"]{8,}"), "Possible literal secret in source"),
    ("path-join-input", re.compile(r"(?:Path\(|path\.join\().*(?:input|request|argument|args)"), "Review user-controlled path resolution and workspace enforcement")
]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.project.expanduser().resolve()
    if not root.is_dir(): parser.error(f"project is not a directory: {root}")
    issues = []
    files = list(iter_files(root, suffixes={".py", ".ts", ".tsx", ".js", ".mjs"}))
    for path in files:
        try: lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError: continue
        for number, line in enumerate(lines, 1):
            for code, pattern, message in PATTERNS:
                if pattern.search(line): issues.append(issue(code, message, severity="warning", path=f"{relative(path, root)}:{number}"))
    corpus = "\n".join(relative(p, root).lower() for p in iter_files(root))
    required = {"permission-control": ("permission", "policy"), "checkpoint-control": ("checkpoint",), "verification-control": ("verif",), "telemetry-control": ("telemetry", "trace", "audit", "metric"), "test-control": ("test",)}
    for code, terms in required.items():
        if not any(term in corpus for term in terms): issues.append(issue(code, f"No file-level evidence found for {code.replace('-', ' ')}", severity="error" if code == "permission-control" else "warning"))
    value = result("audit_agent_safety", root, issues, {"source_files_scanned": len(files), "note": "Static findings require human confirmation; absence is not proof of safety."})
    emit(value, json_output=args.json)
    return 1 if value["status"] == "failed" else 0

if __name__ == "__main__": raise SystemExit(main())

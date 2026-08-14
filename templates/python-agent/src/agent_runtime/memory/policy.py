from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from .contracts import MemoryDecision, MemoryRecord


SECRET_KEY = re.compile(r"(?i)(?:api[_-]?key|password|secret|access[_-]?token|auth[_-]?token|credential)")
SECRET_VALUE = re.compile(r"(?i)(?:\bsk-[a-z0-9_-]{4,}|bearer\s+[a-z0-9._-]+|secret://|vault://)")


def _contains_secret(value: Any, key: str = "") -> bool:
    if key and SECRET_KEY.search(key):
        return True
    if isinstance(value, str):
        return bool(SECRET_VALUE.search(value))
    if isinstance(value, Mapping):
        return any(_contains_secret(item, str(name)) for name, item in value.items())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_contains_secret(item) for item in value)
    return False


class MemoryPolicy:
    def __init__(self, *, consent_required: bool = True, version: str = "1.0") -> None:
        self.consent_required = consent_required
        self.version = version

    def evaluate(self, record: MemoryRecord) -> MemoryDecision:
        consented = record.consented if record.consented is not None else record.consent_basis not in {"", "none"}
        if self.consent_required and not consented:
            return MemoryDecision("reject", "consent_required", self.version)
        if _contains_secret(record.content):
            return MemoryDecision("reject", "secret_material", self.version)
        if not record.summary.strip() and not str(record.content).strip():
            return MemoryDecision("reject", "no_durable_value", self.version)
        if record.sensitivity in {"sensitive", "restricted"}:
            return MemoryDecision("needs_confirmation", "sensitive_memory", self.version)
        return MemoryDecision("accept", "policy_passed", self.version)

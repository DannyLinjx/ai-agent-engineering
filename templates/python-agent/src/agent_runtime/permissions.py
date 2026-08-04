from typing import Literal

class PermissionEngine:
    def decide(self, category: str, risk_level: str) -> Literal["ALLOW", "DENY", "ASK"]:
        if risk_level == "critical": return "DENY"
        if risk_level == "high" or category == "communication": return "ASK"
        return "ALLOW" if category == "read" else "ASK"

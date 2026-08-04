from dataclasses import dataclass

@dataclass(frozen=True)
class ModelProfile:
    id: str
    supports_tools: bool
    supports_json: bool
    privacy: str
    max_context_tokens: int
    cost_tier: int
    healthy: bool

class ModelRouter:
    def __init__(self, profiles: list[ModelProfile]) -> None: self.profiles = profiles
    def select(self, *, tools: bool, json_mode: bool, private_data: bool, input_tokens: int) -> ModelProfile:
        candidates = [p for p in self.profiles if p.healthy and (not tools or p.supports_tools) and (not json_mode or p.supports_json) and (not private_data or p.privacy == "local") and p.max_context_tokens >= input_tokens]
        if not candidates: raise LookupError("no compatible model")
        return min(candidates, key=lambda p: p.cost_tier)

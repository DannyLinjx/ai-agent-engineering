from dataclasses import dataclass
from typing import Protocol

class ModelGateway(Protocol):
    def decide(self, state: object) -> object: ...

@dataclass(frozen=True)
class ProviderAdapter:
    id: str
    type: str
    gateway: ModelGateway

class ProviderRegistry:
    def __init__(self, selection: str) -> None: self.selection, self.providers = selection, {}
    def register(self, provider: ProviderAdapter) -> None:
        if provider.id in self.providers: raise ValueError(f"duplicate provider: {provider.id}")
        self.providers[provider.id] = provider
    def get(self, provider_id: str) -> ProviderAdapter | None: return self.providers.get(provider_id)
    def has_live_provider(self) -> bool: return any(provider.type != "mock" for provider in self.providers.values())

from dataclasses import dataclass, field
from typing import Protocol

@dataclass(frozen=True)
class InboundMessage:
    tenant_id: str
    user_id: str
    channel_id: str
    conversation_id: str
    message_id: str
    text: str
    attachments: list[str] = field(default_factory=list)

@dataclass(frozen=True)
class OutboundMessage:
    conversation_id: str
    text: str
    idempotency_key: str
    artifact_refs: list[str] = field(default_factory=list)

class ChannelAdapter(Protocol):
    id: str
    type: str
    def send(self, message: OutboundMessage) -> str: ...
    def health(self) -> bool: ...
    def stop(self) -> None: ...

class ChannelRegistry:
    def __init__(self) -> None: self.adapters: dict[str, ChannelAdapter] = {}
    def register(self, adapter: ChannelAdapter) -> None:
        if adapter.id in self.adapters: raise ValueError(f"duplicate channel: {adapter.id}")
        self.adapters[adapter.id] = adapter
    def get(self, adapter_id: str) -> ChannelAdapter | None: return self.adapters.get(adapter_id)

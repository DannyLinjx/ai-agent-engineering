from dataclasses import dataclass
from typing import Any, Literal, Protocol
from .contracts import AgentState

@dataclass(frozen=True)
class ToolResult:
    status: Literal["success", "error", "cancelled"]
    summary: str
    retryable: bool = False

class Tool(Protocol):
    name: str
    category: Literal["read", "write", "exec", "network", "database", "browser", "communication"]
    risk_level: Literal["low", "medium", "high", "critical"]
    def execute(self, input_data: Any, state: AgentState) -> ToolResult: ...

class ToolRegistry:
    def __init__(self) -> None: self._tools: dict[str, Tool] = {}
    def register(self, tool: Tool) -> None:
        if tool.name in self._tools: raise ValueError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool
    def get(self, name: str) -> Tool:
        if name not in self._tools: raise KeyError(f"unknown tool: {name}")
        return self._tools[name]

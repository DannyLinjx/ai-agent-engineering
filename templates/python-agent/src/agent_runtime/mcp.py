from typing import Protocol

class McpConnection(Protocol):
    def health(self) -> bool: ...
    def list_tools(self) -> list[dict[str, object]]: ...
    def close(self) -> None: ...

class McpConnector(Protocol):
    def connect(self, server: str) -> McpConnection: ...

class McpClientManager:
    def __init__(self, selection: str, connector: McpConnector, allowed_servers: set[str]) -> None: self.selection, self.connector, self.allowed_servers = selection, connector, allowed_servers
    def is_enabled(self) -> bool: return self.selection == "configured"
    def connect(self, server: str) -> McpConnection:
        if not self.is_enabled(): raise RuntimeError("MCP is not configured")
        if server not in self.allowed_servers: raise PermissionError("MCP server is not allowed")
        return self.connector.connect(server)

from collections import defaultdict
from collections.abc import Callable
from typing import Any

class HookBus:
    def __init__(self) -> None: self.hooks: dict[str, list[tuple[int, Callable[[Any], Any]]]] = defaultdict(list)
    def register(self, event: str, priority: int, hook: Callable[[Any], Any]) -> None: self.hooks[event].append((priority, hook)); self.hooks[event].sort(key=lambda x: x[0])
    def emit(self, event: str, value: Any) -> Any:
        for _, hook in self.hooks[event]: value = hook(value)
        return value

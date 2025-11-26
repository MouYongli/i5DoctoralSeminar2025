"""Base tool infrastructure for Temporal activities."""

import logging
from dataclasses import dataclass
from typing import Any, Callable, Awaitable

logger = logging.getLogger(__name__)


@dataclass
class ToolInput:
    """Input for a tool activity."""

    tool_name: str
    params: dict[str, Any]
    context: dict[str, Any] | None = None


@dataclass
class ToolOutput:
    """Output from a tool activity."""

    success: bool
    result: Any = None
    error: str | None = None


class ToolRegistry:
    """Registry for available tools."""

    def __init__(self):
        self._tools: dict[str, Callable[..., Awaitable[Any]]] = {}

    def register(self, name: str, func: Callable[..., Awaitable[Any]]) -> None:
        """Register a tool function."""
        self._tools[name] = func
        logger.info(f"Registered tool: {name}")

    def get(self, name: str) -> Callable[..., Awaitable[Any]] | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        """List all registered tools."""
        return list(self._tools.keys())


# Global tool registry
_tool_registry: ToolRegistry | None = None


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry."""
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry

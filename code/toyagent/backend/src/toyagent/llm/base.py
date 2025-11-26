"""Base LLM client interface."""

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from toyagent.schemas.workflow import WorkflowSpec


class AgentResponse(BaseModel):
    """Response from the LLM agent."""

    reply: str
    workflow_spec: WorkflowSpec | None = None


class LLMClient(ABC):
    """Abstract base class for LLM clients."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AgentResponse:
        """
        Send messages to LLM and get response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context: Optional context dict for the conversation
            system_prompt: Optional system prompt to override default

        Returns:
            AgentResponse with reply text and optional workflow_spec
        """
        pass

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ):
        """
        Send messages to LLM and stream response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            context: Optional context dict for the conversation
            system_prompt: Optional system prompt to override default

        Yields:
            String chunks of the response
        """
        pass

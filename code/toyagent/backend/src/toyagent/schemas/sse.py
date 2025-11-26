"""SSE event schemas."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel


class SSEEvent(BaseModel):
    """Base SSE event."""

    event: str
    data: dict[str, Any]
    timestamp: datetime | None = None

    def to_sse(self) -> str:
        """Convert to SSE format string."""
        import json

        ts = self.timestamp or datetime.utcnow()
        data = {**self.data, "timestamp": ts.isoformat()}
        return f"event: {self.event}\ndata: {json.dumps(data)}\n\n"


class ChatStreamEvent(BaseModel):
    """Chat streaming event types."""

    event: Literal[
        "message_start",  # Start of message stream
        "content_delta",  # Content chunk
        "message_end",  # End of message stream
        "workflow_created",  # Workflow was created
        "error",  # Error occurred
    ]
    data: dict[str, Any]

    def to_sse(self) -> str:
        """Convert to SSE format string."""
        import json

        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"


class WorkflowStreamEvent(BaseModel):
    """Workflow status streaming event types."""

    event: Literal[
        "workflow_start",  # Workflow started
        "step_start",  # Step started
        "step_progress",  # Step progress update
        "step_complete",  # Step completed
        "step_failed",  # Step failed
        "workflow_complete",  # Workflow completed
        "workflow_failed",  # Workflow failed
        "error",  # Error occurred
    ]
    data: dict[str, Any]

    def to_sse(self) -> str:
        """Convert to SSE format string."""
        import json

        return f"event: {self.event}\ndata: {json.dumps(self.data)}\n\n"

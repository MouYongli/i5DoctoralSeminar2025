"""Message schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class MessageCreate(BaseModel):
    """Schema for creating a new message."""

    content: str
    sender: Literal["user", "agent", "system"] = "user"


class MessageResponse(BaseModel):
    """Schema for message response."""

    id: str
    chat_id: str
    sender: str
    content: str
    related_workflow_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MessageWithWorkflowResponse(BaseModel):
    """Schema for message response with optional workflow."""

    user_message: MessageResponse
    agent_message: MessageResponse | None = None
    workflow: "WorkflowMetaResponse | None" = None


# Import for forward references
from toyagent.schemas.workflow import WorkflowMetaResponse  # noqa: E402

MessageWithWorkflowResponse.model_rebuild()

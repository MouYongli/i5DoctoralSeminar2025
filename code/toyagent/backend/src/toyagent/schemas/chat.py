"""Chat schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatCreate(BaseModel):
    """Schema for creating a new chat."""

    title: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Schema for chat response."""

    id: str
    title: str | None
    context: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    messages: list["MessageResponse"] = []
    workflows: list["WorkflowMetaResponse"] = []

    model_config = {"from_attributes": True}


class ChatListResponse(BaseModel):
    """Schema for listing chats."""

    id: str
    title: str | None
    context: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


# Import for forward references
from toyagent.schemas.message import MessageResponse  # noqa: E402
from toyagent.schemas.workflow import WorkflowMetaResponse  # noqa: E402

ChatResponse.model_rebuild()

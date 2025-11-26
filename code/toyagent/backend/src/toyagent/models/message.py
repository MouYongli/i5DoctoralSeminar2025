"""Message model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from toyagent.database import Base

if TYPE_CHECKING:
    from toyagent.models.chat import Chat
    from toyagent.models.workflow import WorkflowMeta


class Message(Base):
    """Message model representing a single message in a chat."""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    chat_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("chats.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )  # user | agent | system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    related_workflow_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workflow_meta.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    workflow: Mapped["WorkflowMeta | None"] = relationship(
        "WorkflowMeta",
        back_populates="related_messages",
    )

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, sender={self.sender})>"

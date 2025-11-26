"""WorkflowMeta model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from toyagent.database import Base

if TYPE_CHECKING:
    from toyagent.models.chat import Chat
    from toyagent.models.message import Message


class WorkflowMeta(Base):
    """WorkflowMeta model representing a Temporal workflow instance."""

    __tablename__ = "workflow_meta"

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
    temporal_workflow_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
    )  # pending | running | completed | failed
    spec: Mapped[dict] = mapped_column(JSON, nullable=False)  # WorkflowSpec JSON
    steps_status: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )  # {step_id: status}
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    chat: Mapped["Chat"] = relationship("Chat", back_populates="workflows")
    related_messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="workflow",
    )

    def __repr__(self) -> str:
        return f"<WorkflowMeta(id={self.id}, name={self.name}, status={self.status})>"

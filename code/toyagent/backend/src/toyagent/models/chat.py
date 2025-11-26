"""Chat model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from toyagent.database import Base

if TYPE_CHECKING:
    from toyagent.models.message import Message
    from toyagent.models.workflow import WorkflowMeta


class Chat(Base):
    """Chat model representing a conversation session."""

    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    context: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
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
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )
    workflows: Mapped[list["WorkflowMeta"]] = relationship(
        "WorkflowMeta",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="WorkflowMeta.created_at",
    )

    def __repr__(self) -> str:
        return f"<Chat(id={self.id}, title={self.title})>"

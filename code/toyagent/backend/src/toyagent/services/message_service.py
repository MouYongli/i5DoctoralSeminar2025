"""Message service layer."""

from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from toyagent.models import Message
from toyagent.schemas import MessageCreate


class MessageService:
    """Service for managing messages."""

    @staticmethod
    async def create_message(
        db: AsyncSession,
        chat_id: str,
        message_data: MessageCreate,
        related_workflow_id: str | None = None,
    ) -> Message:
        """Create a new message."""
        message = Message(
            id=str(uuid4()),
            chat_id=chat_id,
            sender=message_data.sender,
            content=message_data.content,
            related_workflow_id=related_workflow_id,
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)
        return message

    @staticmethod
    async def get_messages(
        db: AsyncSession,
        chat_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Message]:
        """Get messages for a chat."""
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_recent_messages(
        db: AsyncSession,
        chat_id: str,
        limit: int = 20,
    ) -> list[Message]:
        """Get recent messages for a chat (for LLM context)."""
        result = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = list(result.scalars().all())
        # Reverse to get chronological order
        return messages[::-1]

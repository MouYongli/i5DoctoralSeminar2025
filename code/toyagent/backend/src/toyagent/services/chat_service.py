"""Chat service layer."""

from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from toyagent.models import Chat, Message
from toyagent.schemas import ChatCreate


class ChatService:
    """Service for managing chats."""

    @staticmethod
    async def create_chat(db: AsyncSession, chat_data: ChatCreate) -> Chat:
        """Create a new chat."""
        chat = Chat(
            id=str(uuid4()),
            title=chat_data.title,
            context=chat_data.context,
        )
        db.add(chat)
        await db.commit()
        await db.refresh(chat)
        return chat

    @staticmethod
    async def get_chat(db: AsyncSession, chat_id: str) -> Chat | None:
        """Get a chat by ID with messages and workflows."""
        result = await db.execute(
            select(Chat)
            .options(
                selectinload(Chat.messages),
                selectinload(Chat.workflows),
            )
            .where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_chats(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50,
    ) -> list[tuple[Chat, int]]:
        """Get all chats with message counts."""
        # Subquery for message count
        message_count_subquery = (
            select(Message.chat_id, func.count(Message.id).label("message_count"))
            .group_by(Message.chat_id)
            .subquery()
        )

        result = await db.execute(
            select(Chat, func.coalesce(message_count_subquery.c.message_count, 0))
            .outerjoin(
                message_count_subquery,
                Chat.id == message_count_subquery.c.chat_id,
            )
            .order_by(Chat.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.all())

    @staticmethod
    async def delete_chat(db: AsyncSession, chat_id: str) -> bool:
        """Delete a chat by ID."""
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if chat:
            await db.delete(chat)
            await db.commit()
            return True
        return False

    @staticmethod
    async def update_chat_context(
        db: AsyncSession,
        chat_id: str,
        context: dict,
    ) -> Chat | None:
        """Update chat context."""
        result = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = result.scalar_one_or_none()
        if chat:
            chat.context = context
            await db.commit()
            await db.refresh(chat)
        return chat

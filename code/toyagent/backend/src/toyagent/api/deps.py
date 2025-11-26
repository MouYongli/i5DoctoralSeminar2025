"""API dependencies."""

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession

from toyagent.database import async_session_maker
from toyagent.llm import AzureOpenAIClient, LLMClient


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


@lru_cache
def get_llm_client() -> LLMClient:
    """Get cached LLM client instance."""
    return AzureOpenAIClient()

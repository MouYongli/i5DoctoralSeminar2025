"""Chat API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from toyagent.api.deps import get_db, get_llm_client
from toyagent.llm import LLMClient
from toyagent.schemas import (
    ChatCreate,
    ChatListResponse,
    ChatResponse,
    MessageCreate,
    MessageResponse,
    MessageWithWorkflowResponse,
    WorkflowMetaResponse,
)
from toyagent.services import ChatService, MessageService, WorkflowService
from toyagent.temporal import start_workflow

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat",
)
async def create_chat(
    chat_data: ChatCreate,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Create a new chat session."""
    chat = await ChatService.create_chat(db, chat_data)
    return ChatResponse(
        id=chat.id,
        title=chat.title,
        context=chat.context,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        messages=[],
        workflows=[],
    )


@router.get(
    "",
    response_model=list[ChatListResponse],
    summary="List all chats",
)
async def list_chats(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[ChatListResponse]:
    """List all chat sessions."""
    chats_with_counts = await ChatService.get_chats(db, skip=skip, limit=limit)
    return [
        ChatListResponse(
            id=chat.id,
            title=chat.title,
            context=chat.context,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            message_count=count,
        )
        for chat, count in chats_with_counts
    ]


@router.get(
    "/{chat_id}",
    response_model=ChatResponse,
    summary="Get a chat by ID",
)
async def get_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    """Get a chat session by ID with all messages and workflows."""
    chat = await ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found",
        )
    return ChatResponse.model_validate(chat)


@router.delete(
    "/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat",
)
async def delete_chat(
    chat_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a chat session and all its messages/workflows."""
    deleted = await ChatService.delete_chat(db, chat_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found",
        )


@router.post(
    "/{chat_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a message to a chat",
)
async def add_message(
    chat_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Add a message to a chat session (simple, no LLM)."""
    # Verify chat exists
    chat = await ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found",
        )

    message = await MessageService.create_message(db, chat_id, message_data)
    return MessageResponse.model_validate(message)


@router.get(
    "/{chat_id}/messages",
    response_model=list[MessageResponse],
    summary="Get messages for a chat",
)
async def get_messages(
    chat_id: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
) -> list[MessageResponse]:
    """Get all messages for a chat session."""
    # Verify chat exists
    chat = await ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found",
        )

    messages = await MessageService.get_messages(db, chat_id, skip=skip, limit=limit)
    return [MessageResponse.model_validate(msg) for msg in messages]


@router.post(
    "/{chat_id}/chat",
    response_model=MessageWithWorkflowResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send a message and get LLM response",
)
async def chat_with_llm(
    chat_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client),
) -> MessageWithWorkflowResponse:
    """
    Send a user message and get an LLM response.

    This is the main chat endpoint that:
    1. Saves the user message
    2. Gets recent messages for context
    3. Calls the LLM
    4. Saves and returns the agent response
    """
    # Verify chat exists
    chat = await ChatService.get_chat(db, chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chat {chat_id} not found",
        )

    # Save user message
    user_message = await MessageService.create_message(
        db,
        chat_id,
        MessageCreate(content=message_data.content, sender="user"),
    )

    # Get recent messages for context
    recent_messages = await MessageService.get_recent_messages(db, chat_id, limit=20)

    # Build message list for LLM
    llm_messages = [
        {"role": msg.sender, "content": msg.content} for msg in recent_messages
    ]

    # Call LLM
    agent_response = await llm.chat(
        messages=llm_messages,
        context=chat.context,
    )

    # Save agent response
    agent_message = await MessageService.create_message(
        db,
        chat_id,
        MessageCreate(content=agent_response.reply, sender="agent"),
    )

    # If workflow_spec exists, create WorkflowMeta and start Temporal workflow
    workflow_response = None
    if agent_response.workflow_spec:
        try:
            spec_dict = agent_response.workflow_spec.model_dump()

            # Start Temporal workflow
            temporal_workflow_id = await start_workflow(
                chat_id=chat_id,
                spec=spec_dict,
                context=chat.context,
            )

            # Create workflow metadata in database
            workflow_meta = await WorkflowService.create_workflow(
                db=db,
                chat_id=chat_id,
                temporal_workflow_id=temporal_workflow_id,
                name=agent_response.workflow_spec.name,
                spec=spec_dict,
            )

            # Update agent message with workflow reference
            agent_message.related_workflow_id = workflow_meta.id
            await db.commit()

            workflow_response = WorkflowMetaResponse.model_validate(workflow_meta)
            logger.info(f"Started workflow {temporal_workflow_id} for chat {chat_id}")

        except Exception as e:
            logger.exception(f"Failed to start workflow: {e}")
            # Continue without workflow - the message is still saved

    return MessageWithWorkflowResponse(
        user_message=MessageResponse.model_validate(user_message),
        agent_message=MessageResponse.model_validate(agent_message),
        workflow=workflow_response,
    )

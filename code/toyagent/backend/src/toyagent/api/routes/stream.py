"""Streaming API routes using SSE."""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from toyagent.api.deps import get_db, get_llm_client
from toyagent.llm import LLMClient
from toyagent.schemas import MessageCreate, WorkflowMetaResponse
from toyagent.services import ChatService, MessageService, WorkflowService
from toyagent.temporal import start_workflow
from toyagent.temporal.client import get_workflow_status

logger = logging.getLogger(__name__)

router = APIRouter()


async def chat_stream_generator(
    chat_id: str,
    content: str,
    db: AsyncSession,
    llm: LLMClient,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for chat streaming."""

    # Verify chat exists
    chat = await ChatService.get_chat(db, chat_id)
    if not chat:
        yield f"event: error\ndata: {json.dumps({'error': f'Chat {chat_id} not found'})}\n\n"
        return

    # Save user message
    user_message = await MessageService.create_message(
        db,
        chat_id,
        MessageCreate(content=content, sender="user"),
    )

    # Send user message confirmation
    yield f"event: message_start\ndata: {json.dumps({'type': 'user', 'message_id': str(user_message.id)})}\n\n"

    # Get recent messages for context
    recent_messages = await MessageService.get_recent_messages(db, chat_id, limit=20)
    llm_messages = [
        {"role": msg.sender, "content": msg.content} for msg in recent_messages
    ]

    # Stream LLM response
    full_content = ""
    yield f"event: message_start\ndata: {json.dumps({'type': 'agent'})}\n\n"

    try:
        async for chunk in llm.chat_stream(
            messages=llm_messages,
            context=chat.context,
        ):
            full_content += chunk
            yield f"event: content_delta\ndata: {json.dumps({'content': chunk})}\n\n"

        # Save agent response
        agent_message = await MessageService.create_message(
            db,
            chat_id,
            MessageCreate(content=full_content, sender="agent"),
        )

        # Check if response contains workflow spec
        from toyagent.llm.azure_openai import AzureOpenAIClient

        client = AzureOpenAIClient()
        workflow_spec = client._extract_workflow_spec(full_content)

        workflow_response = None
        if workflow_spec:
            try:
                spec_dict = workflow_spec.model_dump()

                # Start Temporal workflow
                temporal_workflow_id = await start_workflow(
                    chat_id=chat_id,
                    spec=spec_dict,
                    context=chat.context,
                )

                # Create workflow metadata
                workflow_meta = await WorkflowService.create_workflow(
                    db=db,
                    chat_id=chat_id,
                    temporal_workflow_id=temporal_workflow_id,
                    name=workflow_spec.name,
                    spec=spec_dict,
                )

                # Update agent message with workflow reference
                agent_message.related_workflow_id = workflow_meta.id
                await db.commit()

                workflow_response = WorkflowMetaResponse.model_validate(workflow_meta)

                yield f"event: workflow_created\ndata: {json.dumps(workflow_response.model_dump(mode='json'))}\n\n"

            except Exception as e:
                logger.exception(f"Failed to start workflow: {e}")

        yield f"event: message_end\ndata: {json.dumps({'message_id': str(agent_message.id), 'has_workflow': workflow_response is not None})}\n\n"

    except Exception as e:
        logger.exception(f"Error during chat stream: {e}")
        yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"


@router.post(
    "/chats/{chat_id}/stream",
    summary="Stream chat response via SSE",
)
async def stream_chat(
    chat_id: str,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    llm: LLMClient = Depends(get_llm_client),
):
    """
    Stream a chat response using Server-Sent Events.

    Events:
    - message_start: Start of a message (user or agent)
    - content_delta: Content chunk from LLM
    - message_end: End of message with message_id
    - workflow_created: Workflow was created from response
    - error: An error occurred
    """
    return EventSourceResponse(
        chat_stream_generator(chat_id, message_data.content, db, llm),
        media_type="text/event-stream",
    )


async def workflow_status_generator(
    workflow_id: str,
    db: AsyncSession,
    poll_interval: float = 1.0,
) -> AsyncGenerator[str, None]:
    """Generate SSE events for workflow status updates."""

    # Get workflow from database
    workflow = await WorkflowService.get_workflow(db, workflow_id)
    if not workflow:
        yield f"event: error\ndata: {json.dumps({'error': f'Workflow {workflow_id} not found'})}\n\n"
        return

    yield f"event: workflow_start\ndata: {json.dumps({'workflow_id': workflow_id, 'name': workflow.name, 'status': workflow.status})}\n\n"

    last_step_statuses = {}
    last_status = workflow.status

    # Poll for status updates
    while True:
        try:
            # Query Temporal for live status
            temporal_status = await get_workflow_status(workflow.temporal_workflow_id)

            if temporal_status:
                current_step = temporal_status.get("current_step")
                step_statuses = temporal_status.get("step_statuses", {})

                # Check for step status changes
                for step_id, step_status in step_statuses.items():
                    if step_id not in last_step_statuses:
                        yield f"event: step_start\ndata: {json.dumps({'step_id': step_id, 'status': step_status})}\n\n"
                    elif last_step_statuses[step_id] != step_status:
                        if step_status == "completed":
                            yield f"event: step_complete\ndata: {json.dumps({'step_id': step_id})}\n\n"
                        elif step_status == "failed":
                            yield f"event: step_failed\ndata: {json.dumps({'step_id': step_id})}\n\n"
                        else:
                            yield f"event: step_progress\ndata: {json.dumps({'step_id': step_id, 'status': step_status})}\n\n"

                last_step_statuses = step_statuses.copy()

                # Check if workflow completed or failed
                all_completed = all(s == "completed" for s in step_statuses.values()) if step_statuses else False
                any_failed = any(s == "failed" for s in step_statuses.values()) if step_statuses else False

                if any_failed and last_status != "failed":
                    last_status = "failed"
                    await WorkflowService.update_workflow_status(db, workflow_id, "failed", step_statuses)
                    yield f"event: workflow_failed\ndata: {json.dumps({'workflow_id': workflow_id, 'step_statuses': step_statuses})}\n\n"
                    break
                elif all_completed and step_statuses and last_status != "completed":
                    last_status = "completed"
                    await WorkflowService.update_workflow_status(db, workflow_id, "completed", step_statuses)
                    yield f"event: workflow_complete\ndata: {json.dumps({'workflow_id': workflow_id, 'step_statuses': step_statuses})}\n\n"
                    break

            await asyncio.sleep(poll_interval)

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception(f"Error polling workflow status: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"
            break


@router.get(
    "/workflows/{workflow_id}/stream",
    summary="Stream workflow status via SSE",
)
async def stream_workflow_status(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream workflow execution status using Server-Sent Events.

    Events:
    - workflow_start: Workflow info at connection
    - step_start: A step has started
    - step_progress: Step progress update
    - step_complete: A step completed
    - step_failed: A step failed
    - workflow_complete: Workflow completed successfully
    - workflow_failed: Workflow failed
    - error: An error occurred
    """
    return EventSourceResponse(
        workflow_status_generator(workflow_id, db),
        media_type="text/event-stream",
    )

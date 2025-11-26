"""Temporal client helper functions."""

import logging
import uuid
from functools import lru_cache
from typing import Any

from temporalio.client import Client

from toyagent.config import get_settings
from toyagent.temporal.workflows import JsonWorkflow, JsonWorkflowInput

logger = logging.getLogger(__name__)

TASK_QUEUE = "toyagent-tasks"


@lru_cache
def _get_settings():
    return get_settings()


async def get_temporal_client() -> Client:
    """Get Temporal client instance."""
    settings = _get_settings()
    client = await Client.connect(settings.temporal_address, namespace=settings.temporal_namespace)
    return client


async def start_workflow(
    chat_id: str,
    spec: dict[str, Any],
    context: dict[str, Any] | None = None,
) -> str:
    """
    Start a JsonWorkflow.

    Args:
        chat_id: The chat ID this workflow belongs to
        spec: The workflow specification
        context: Optional context for the workflow

    Returns:
        The Temporal workflow ID
    """
    client = await get_temporal_client()

    workflow_id = f"toyagent-{chat_id}-{uuid.uuid4().hex[:8]}"

    input_data = JsonWorkflowInput(
        workflow_id=workflow_id,
        chat_id=chat_id,
        spec=spec,
        context=context,
    )

    handle = await client.start_workflow(
        JsonWorkflow.run,
        input_data,
        id=workflow_id,
        task_queue=TASK_QUEUE,
    )

    logger.info(f"Started workflow {workflow_id} for chat {chat_id}")
    return handle.id


async def get_workflow_status(workflow_id: str) -> dict[str, Any] | None:
    """
    Get the status of a running workflow.

    Args:
        workflow_id: The Temporal workflow ID

    Returns:
        Workflow status dict or None if not found
    """
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)

        # Query the workflow for status
        status = await handle.query(JsonWorkflow.get_status)
        return status
    except Exception as e:
        logger.warning(f"Failed to get workflow status for {workflow_id}: {e}")
        return None


async def get_workflow_result(workflow_id: str) -> dict[str, Any] | None:
    """
    Get the result of a completed workflow.

    Args:
        workflow_id: The Temporal workflow ID

    Returns:
        Workflow result dict or None if not completed/found
    """
    try:
        client = await get_temporal_client()
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.result()
        return result
    except Exception as e:
        logger.warning(f"Failed to get workflow result for {workflow_id}: {e}")
        return None

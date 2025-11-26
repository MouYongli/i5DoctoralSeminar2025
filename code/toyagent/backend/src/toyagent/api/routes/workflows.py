"""Workflow API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from toyagent.api.deps import get_db
from toyagent.schemas import WorkflowMetaResponse
from toyagent.services import WorkflowService
from toyagent.temporal.client import get_workflow_status, get_workflow_result

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{workflow_id}",
    response_model=WorkflowMetaResponse,
    summary="Get workflow by ID",
)
async def get_workflow(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> WorkflowMetaResponse:
    """Get workflow metadata by ID."""
    workflow = await WorkflowService.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )
    return WorkflowMetaResponse.model_validate(workflow)


@router.get(
    "/{workflow_id}/status",
    summary="Get workflow execution status",
)
async def get_workflow_execution_status(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get the real-time execution status of a workflow from Temporal.

    Returns the current step, step statuses, and intermediate results.
    """
    # First get the workflow metadata to get temporal_workflow_id
    workflow = await WorkflowService.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Query Temporal for live status
    temporal_status = await get_workflow_status(workflow.temporal_workflow_id)

    if temporal_status:
        # Update database with latest status
        step_statuses = temporal_status.get("step_statuses", {})
        all_completed = all(s == "completed" for s in step_statuses.values()) if step_statuses else False
        any_failed = any(s == "failed" for s in step_statuses.values()) if step_statuses else False

        if any_failed:
            new_status = "failed"
        elif all_completed and step_statuses:
            new_status = "completed"
        elif any(s == "running" for s in step_statuses.values()):
            new_status = "running"
        else:
            new_status = workflow.status

        if new_status != workflow.status or step_statuses != workflow.steps_status:
            await WorkflowService.update_workflow_status(
                db, workflow_id, new_status, step_statuses
            )

        return {
            "workflow_id": workflow_id,
            "temporal_workflow_id": workflow.temporal_workflow_id,
            "status": new_status,
            "current_step": temporal_status.get("current_step"),
            "step_statuses": step_statuses,
        }

    # If we can't query Temporal, return what we have in database
    return {
        "workflow_id": workflow_id,
        "temporal_workflow_id": workflow.temporal_workflow_id,
        "status": workflow.status,
        "current_step": None,
        "step_statuses": workflow.steps_status,
    }


@router.get(
    "/{workflow_id}/result",
    summary="Get workflow result",
)
async def get_workflow_execution_result(
    workflow_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Get the final result of a completed workflow.

    Only available after workflow completes (successfully or with failure).
    """
    workflow = await WorkflowService.get_workflow(db, workflow_id)
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found",
        )

    # Get result from Temporal
    result = await get_workflow_result(workflow.temporal_workflow_id)

    if result:
        # Update workflow status based on result
        new_status = "completed" if result.get("success") else "failed"
        if new_status != workflow.status:
            await WorkflowService.update_workflow_status(
                db, workflow_id, new_status, result.get("step_statuses", {})
            )

        return {
            "workflow_id": workflow_id,
            "temporal_workflow_id": workflow.temporal_workflow_id,
            "success": result.get("success", False),
            "results": result.get("results", {}),
            "step_statuses": result.get("step_statuses", {}),
            "error": result.get("error"),
        }

    return {
        "workflow_id": workflow_id,
        "temporal_workflow_id": workflow.temporal_workflow_id,
        "status": workflow.status,
        "message": "Workflow result not yet available. Workflow may still be running.",
    }

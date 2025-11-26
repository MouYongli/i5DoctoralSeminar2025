"""Workflow service for managing workflow metadata."""

import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from toyagent.models import WorkflowMeta

logger = logging.getLogger(__name__)


class WorkflowService:
    """Service for workflow metadata operations."""

    @staticmethod
    async def create_workflow(
        db: AsyncSession,
        chat_id: str,
        temporal_workflow_id: str,
        name: str,
        spec: dict[str, Any],
    ) -> WorkflowMeta:
        """Create a new workflow metadata record."""
        workflow = WorkflowMeta(
            chat_id=chat_id,
            temporal_workflow_id=temporal_workflow_id,
            name=name,
            status="pending",
            spec=spec,
            steps_status={},
        )
        db.add(workflow)
        await db.commit()
        await db.refresh(workflow)
        logger.info(f"Created workflow {workflow.id} for chat {chat_id}")
        return workflow

    @staticmethod
    async def get_workflow(db: AsyncSession, workflow_id: str) -> WorkflowMeta | None:
        """Get a workflow by ID."""
        result = await db.execute(
            select(WorkflowMeta).where(WorkflowMeta.id == workflow_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_workflow_by_temporal_id(
        db: AsyncSession, temporal_workflow_id: str
    ) -> WorkflowMeta | None:
        """Get a workflow by Temporal workflow ID."""
        result = await db.execute(
            select(WorkflowMeta).where(
                WorkflowMeta.temporal_workflow_id == temporal_workflow_id
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_workflows_for_chat(
        db: AsyncSession, chat_id: str
    ) -> list[WorkflowMeta]:
        """Get all workflows for a chat."""
        result = await db.execute(
            select(WorkflowMeta)
            .where(WorkflowMeta.chat_id == chat_id)
            .order_by(WorkflowMeta.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def update_workflow_status(
        db: AsyncSession,
        workflow_id: str,
        status: str,
        steps_status: dict[str, str] | None = None,
    ) -> WorkflowMeta | None:
        """Update workflow status."""
        workflow = await WorkflowService.get_workflow(db, workflow_id)
        if not workflow:
            return None

        workflow.status = status
        if steps_status is not None:
            workflow.steps_status = steps_status

        await db.commit()
        await db.refresh(workflow)
        logger.info(f"Updated workflow {workflow_id} status to {status}")
        return workflow

    @staticmethod
    async def update_workflow_by_temporal_id(
        db: AsyncSession,
        temporal_workflow_id: str,
        status: str,
        steps_status: dict[str, str] | None = None,
    ) -> WorkflowMeta | None:
        """Update workflow status by Temporal workflow ID."""
        workflow = await WorkflowService.get_workflow_by_temporal_id(
            db, temporal_workflow_id
        )
        if not workflow:
            return None

        workflow.status = status
        if steps_status is not None:
            workflow.steps_status = steps_status

        await db.commit()
        await db.refresh(workflow)
        logger.info(f"Updated workflow {temporal_workflow_id} status to {status}")
        return workflow

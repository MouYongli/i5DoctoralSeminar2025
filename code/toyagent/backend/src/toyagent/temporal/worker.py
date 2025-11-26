"""Temporal worker for ToyAgent."""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from toyagent.config import get_settings
from toyagent.temporal.activities import send_email, call_llm, search_web
from toyagent.temporal.workflows import JsonWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TASK_QUEUE = "toyagent-tasks"


async def run_worker():
    """Run the Temporal worker."""
    settings = get_settings()

    logger.info(f"Connecting to Temporal at {settings.temporal_address}")
    client = await Client.connect(
        settings.temporal_address,
        namespace=settings.temporal_namespace,
    )

    logger.info(f"Starting worker on task queue: {TASK_QUEUE}")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[JsonWorkflow],
        activities=[send_email, call_llm, search_web],
    )

    logger.info("Worker started, waiting for tasks...")
    await worker.run()


def main():
    """Entry point for the worker."""
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()

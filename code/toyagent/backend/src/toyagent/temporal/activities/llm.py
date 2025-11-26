"""LLM tool for Temporal workflows."""

import logging
from typing import Any

from temporalio import activity

from toyagent.llm import AzureOpenAIClient

logger = logging.getLogger(__name__)


@activity.defn
async def call_llm(params: dict[str, Any]) -> dict[str, Any]:
    """
    Call LLM as a workflow step.

    Args:
        params: Dictionary containing:
            - prompt: The prompt to send to LLM
            - instruction: Alternative to prompt (LLM-generated workflows may use this)
            - context: Optional context dict or string from previous step
            - system_prompt: Optional system prompt override
            - messages: Optional list of message dicts for conversation

    Returns:
        Dictionary with success status and LLM response
    """
    try:
        client = AzureOpenAIClient()

        # Handle various input formats from LLM-generated workflows
        prompt = params.get("prompt", "")
        instruction = params.get("instruction", "")
        context = params.get("context")
        system_prompt = params.get("system_prompt")
        messages = params.get("messages", [])

        # Build prompt from instruction and context if prompt not provided
        if not prompt and instruction:
            prompt = instruction
            if context:
                # If context is from a previous step result, include it
                if isinstance(context, dict):
                    context_str = str(context)
                else:
                    context_str = str(context)
                prompt = f"Context:\n{context_str}\n\nInstruction: {instruction}"

        # If no messages provided, create one from prompt
        if not messages and prompt:
            messages = [{"role": "user", "content": prompt}]

        if not messages:
            return {
                "success": False,
                "error": "No prompt or messages provided",
            }

        # Call LLM (don't pass context again if already in prompt)
        response = await client.chat(
            messages=messages,
            context=None,  # Context already included in prompt
            system_prompt=system_prompt,
        )

        logger.info(f"LLM call successful, reply length: {len(response.reply)}")
        return {
            "success": True,
            "reply": response.reply,
            "has_workflow": response.workflow_spec is not None,
        }

    except Exception as e:
        logger.exception(f"Failed to call LLM: {e}")
        return {
            "success": False,
            "error": f"Failed to call LLM: {str(e)}",
        }


@activity.defn
async def search_web(params: dict[str, Any]) -> dict[str, Any]:
    """
    Search the web (placeholder for future implementation).

    Args:
        params: Dictionary containing:
            - query: Search query

    Returns:
        Dictionary with search results
    """
    query = params.get("query", "")
    logger.info(f"Web search requested for: {query}")

    # Placeholder - return mock results
    return {
        "success": True,
        "query": query,
        "results": [
            {
                "title": f"Result for: {query}",
                "snippet": "This is a placeholder search result.",
                "url": "https://example.com",
            }
        ],
        "message": "Web search is not yet implemented. This is a placeholder.",
    }

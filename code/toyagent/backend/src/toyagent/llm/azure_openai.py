"""Azure OpenAI client implementation."""

import json
import logging
from typing import Any, AsyncIterator

from openai import AsyncAzureOpenAI

from toyagent.config import get_settings
from toyagent.llm.base import AgentResponse, LLMClient
from toyagent.schemas.workflow import WorkflowSpec

logger = logging.getLogger(__name__)

# System prompt for the agent
DEFAULT_SYSTEM_PROMPT = """You are a helpful AI assistant that can help users with various tasks.

When you determine that a user's request requires tool calls (like sending email, web search), you should generate a workflow specification in JSON format. The workflow spec should be wrapped in a ```workflow code block.

## Available Tools

1. **send_email** - Send an email
   - Parameters:
     - to: Email address(es) of recipient(s) (string or list)
     - subject: Email subject line
     - body: Email body text
     - cc: (optional) CC recipients
     - bcc: (optional) BCC recipients

2. **search_web** - Search the web for information
   - Parameters:
     - query: Search query string
     - num_results: (optional) Number of results to return (default: 5)

3. **call_llm** - Call an LLM for reasoning or text generation
   - Parameters:
     - instruction: The instruction/prompt for the LLM
     - context: (optional) Additional context

## Workflow Spec Format

```workflow
{
  "name": "workflow_name",
  "version": "1.0",
  "steps": [
    {
      "id": "step_1",
      "type": "tool",
      "title": "Step description",
      "uses": "tool_name",
      "input": {"param": "value"},
      "output_key": "result_1"
    }
  ]
}
```

## Example: Send Email

When user asks to send an email, generate a workflow like this:

```workflow
{
  "name": "send_email_workflow",
  "version": "1.0",
  "steps": [
    {
      "id": "send_email",
      "type": "tool",
      "title": "Send email to recipient",
      "uses": "send_email",
      "input": {
        "to": "recipient@example.com",
        "subject": "Email Subject",
        "body": "Email body content here..."
      },
      "output_key": "email_result"
    }
  ]
}
```

## Important Notes

- For email requests, you MUST generate a workflow with the send_email tool
- Extract the recipient, subject, and body from the user's message
- If the user doesn't specify a subject, generate an appropriate one
- Always confirm what you're going to do before generating the workflow
- For simple questions that don't require tools, just respond directly
"""


class AzureOpenAIClient(LLMClient):
    """Azure OpenAI client implementation."""

    def __init__(
        self,
        endpoint: str | None = None,
        api_key: str | None = None,
        deployment: str | None = None,
        api_version: str | None = None,
    ):
        """Initialize Azure OpenAI client."""
        settings = get_settings()

        self.endpoint = endpoint or settings.azure_openai_endpoint
        self.api_key = api_key or settings.azure_openai_api_key
        self.deployment = deployment or settings.azure_openai_deployment
        self.api_version = api_version or settings.azure_openai_api_version

        if not all([self.endpoint, self.api_key, self.deployment]):
            raise ValueError(
                "Azure OpenAI configuration is incomplete. "
                "Please set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, "
                "and AZURE_OPENAI_DEPLOYMENT environment variables."
            )

        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def _build_messages(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> list[dict[str, str]]:
        """Build the message list for the API call."""
        system = system_prompt or DEFAULT_SYSTEM_PROMPT

        # Add context to system prompt if provided
        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            system += f"\n\nCurrent context:\n```json\n{context_str}\n```"

        result = [{"role": "system", "content": system}]

        # Convert message format
        for msg in messages:
            role = msg.get("role", msg.get("sender", "user"))
            # Map sender types to OpenAI roles
            if role == "agent":
                role = "assistant"
            elif role == "system":
                role = "system"
            else:
                role = "user"

            result.append({"role": role, "content": msg.get("content", "")})

        return result

    def _extract_workflow_spec(self, content: str) -> WorkflowSpec | None:
        """Extract workflow spec from response content."""
        import re

        # Look for workflow code block
        pattern = r"```workflow\s*([\s\S]*?)```"
        match = re.search(pattern, content)

        if not match:
            return None

        try:
            spec_json = match.group(1).strip()
            spec_dict = json.loads(spec_json)
            return WorkflowSpec.model_validate(spec_dict)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse workflow spec: {e}")
            return None

    def _clean_response(self, content: str) -> str:
        """Remove workflow code block from response."""
        import re

        # Remove workflow code block
        pattern = r"```workflow\s*[\s\S]*?```"
        return re.sub(pattern, "", content).strip()

    async def chat(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AgentResponse:
        """Send messages to Azure OpenAI and get response."""
        api_messages = self._build_messages(messages, context, system_prompt)

        response = await self.client.chat.completions.create(
            model=self.deployment,
            messages=api_messages,
            temperature=0.7,
            max_tokens=4096,
        )

        content = response.choices[0].message.content or ""

        # Extract workflow spec if present
        workflow_spec = self._extract_workflow_spec(content)

        # Clean response (remove workflow block)
        reply = self._clean_response(content) if workflow_spec else content

        return AgentResponse(reply=reply, workflow_spec=workflow_spec)

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        context: dict[str, Any] | None = None,
        system_prompt: str | None = None,
    ) -> AsyncIterator[str]:
        """Send messages to Azure OpenAI and stream response."""
        api_messages = self._build_messages(messages, context, system_prompt)

        stream = await self.client.chat.completions.create(
            model=self.deployment,
            messages=api_messages,
            temperature=0.7,
            max_tokens=4096,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

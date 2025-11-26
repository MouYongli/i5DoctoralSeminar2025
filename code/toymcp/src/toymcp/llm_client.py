"""
LLM Client - Azure OpenAI Client Wrapper

Provides a high-level interface for interacting with Azure OpenAI, supporting multi-turn conversations and tool calling
"""

import json
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from openai import AzureOpenAI


class LLMClient:
    """Azure OpenAI Client Wrapper Class"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: Optional[str] = None,
    ):
        """
        Initialize LLM client

        Args:
            api_key: Azure OpenAI API key
            api_base: Azure OpenAI API endpoint
            api_version: API version
            deployment_name: Model deployment name
        """
        # Load environment variables
        load_dotenv()

        # Configuration parameters (prioritize passed parameters, otherwise read from environment variables)
        self.api_key = api_key or os.getenv("AZURE_API_KEY")
        self.api_base = api_base or os.getenv("AZURE_API_BASE")
        self.api_version = api_version or os.getenv("AZURE_API_VERSION", "2025-04-01-preview")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-5-chat")

        # Validate required parameters
        if not self.api_key:
            raise ValueError("AZURE_API_KEY is required")
        if not self.api_base:
            raise ValueError("AZURE_API_BASE is required")

        # Initialize Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.api_base,
        )

        # Message history
        self.messages: List[Dict[str, Any]] = []

        # Available tools list
        self.tools: List[Dict[str, Any]] = []

    def set_system_message(self, content: str) -> None:
        """
        Set system message

        Args:
            content: System message content
        """
        # If system message already exists, replace it
        if self.messages and self.messages[0].get("role") == "system":
            self.messages[0]["content"] = content
        else:
            self.messages.insert(0, {"role": "system", "content": content})

    def add_user_message(self, content: str) -> None:
        """
        Add user message

        Args:
            content: User message content
        """
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: Optional[str] = None, tool_calls: Optional[List] = None) -> None:
        """
        Add assistant message

        Args:
            content: Assistant message content
            tool_calls: Tool call list
        """
        message = {"role": "assistant"}
        # Azure OpenAI requires content to be a string, cannot be null
        message["content"] = content if content is not None else ""
        if tool_calls:
            message["tool_calls"] = tool_calls
        self.messages.append(message)

    def add_tool_message(self, tool_call_id: str, content: str) -> None:
        """
        Add tool return message

        Args:
            tool_call_id: Tool call ID
            content: Tool return content
        """
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })

    def set_tools(self, mcp_tools: List[Any]) -> None:
        """
        Set available tools (convert from MCP tools to OpenAI function calling format)

        Args:
            mcp_tools: MCP tool list
        """
        self.tools = []
        for tool in mcp_tools:
            openai_tool = self._convert_mcp_tool_to_openai(tool)
            self.tools.append(openai_tool)

    def _convert_mcp_tool_to_openai(self, mcp_tool: Any) -> Dict[str, Any]:
        """
        Convert MCP tool to OpenAI function calling format

        Args:
            mcp_tool: MCP tool object

        Returns:
            Tool definition in OpenAI function format
        """
        # MCP Tool format:
        # {
        #     "name": "tool_name",
        #     "description": "tool description",
        #     "inputSchema": {
        #         "type": "object",
        #         "properties": {...},
        #         "required": [...]
        #     }
        # }

        return {
            "type": "function",
            "function": {
                "name": mcp_tool.name,
                "description": mcp_tool.description or "",
                "parameters": mcp_tool.inputSchema if hasattr(mcp_tool, 'inputSchema') else {
                    "type": "object",
                    "properties": {},
                }
            }
        }

    def chat(self, user_message: Optional[str] = None, max_tokens: int = 4000, temperature: float = 0.7) -> Any:
        """
        Send message and get response

        Args:
            user_message: User message (if None, use existing message history)
            max_tokens: Maximum number of tokens
            temperature: Temperature parameter

        Returns:
            OpenAI response object
        """
        # If new message provided, add to history
        if user_message:
            self.add_user_message(user_message)

        # Prepare request parameters
        kwargs = {
            "model": self.deployment_name,
            "messages": self.messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        # If tools available, add to request
        if self.tools:
            kwargs["tools"] = self.tools
            kwargs["tool_choice"] = "auto"

        # Call API
        response = self.client.chat.completions.create(**kwargs)

        return response

    def get_last_message_content(self) -> Optional[str]:
        """
        Get last message content

        Returns:
            Last message content, or None if none exists
        """
        if not self.messages:
            return None
        return self.messages[-1].get("content")

    def clear_history(self) -> None:
        """Clear message history (keep system message)"""
        system_message = None
        if self.messages and self.messages[0].get("role") == "system":
            system_message = self.messages[0]

        self.messages = []
        if system_message:
            self.messages.append(system_message)

    def get_message_count(self) -> int:
        """Get message count"""
        return len(self.messages)

    def format_tool_result(self, result: Any) -> str:
        """
        Format tool return result

        Args:
            result: Tool return result

        Returns:
            Formatted string
        """
        if isinstance(result, str):
            return result
        elif isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return str(result)

"""
Chat Agent - Intelligent Conversation Engine

Connects MCP Server and LLM Client to implement tool calling and conversation management
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from toymcp.client import MCPClient
from toymcp.llm_client import LLMClient


class ChatAgent:
    """Intelligent Conversation Agent"""

    def __init__(
        self,
        mcp_client: MCPClient,
        llm_client: LLMClient,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize conversation agent

        Args:
            mcp_client: MCP client instance
            llm_client: LLM client instance
            system_prompt: System prompt
        """
        self.mcp_client = mcp_client
        self.llm_client = llm_client

        # Set default system prompt
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()
        self.llm_client.set_system_message(system_prompt)

    def _get_default_system_prompt(self) -> str:
        """Get default system prompt"""
        return """You are an intelligent study notes assistant that helps users manage study notes and learning progress.

You have the following capabilities:
1. File operations: Create, read, delete study note files
2. File management: List all note files
3. Calculation functions: Help users perform mathematical calculations (such as learning progress percentage)
4. Prompt templates: Provide templates for code review, debugging assistance, etc.

Usage guidelines:
- When users want to create notes, use the create_file tool
- When users want to view notes, use the read_file tool
- When users want to know how many notes they have, use the list_files tool
- When users need calculations, use the calculate tool
- Proactively ask users what help they need
- Communicate with users in a friendly and professional manner
- Use English and underscores for filenames, for example "python_learning.txt"
"""

    async def initialize(self) -> None:
        """Initialize agent (load MCP tools)"""
        # Get available tools from MCP server
        tools = await self.mcp_client.list_tools()

        # Set to LLM client
        self.llm_client.set_tools(tools)

        click.echo(f"✓ Loaded {len(tools)} tools", err=True)

    async def chat(self, user_message: str) -> str:
        """
        Process user message and return response

        Args:
            user_message: User input message

        Returns:
            Assistant's response
        """
        # Send message to LLM
        response = self.llm_client.chat(user_message)

        # Get response message
        message = response.choices[0].message

        # Check if tool call is needed
        if message.tool_calls:
            # Add assistant message (including tool call)
            self.llm_client.add_assistant_message(
                content=message.content,
                tool_calls=[
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in message.tool_calls
                ]
            )

            # Process each tool call
            for tool_call in message.tool_calls:
                # Execute tool call
                tool_result = await self._execute_tool_call(tool_call)

                # Add tool return message
                self.llm_client.add_tool_message(
                    tool_call_id=tool_call.id,
                    content=tool_result,
                )

            # Call LLM again to get final response
            final_response = self.llm_client.chat()
            final_message = final_response.choices[0].message

            # Add final assistant message
            self.llm_client.add_assistant_message(content=final_message.content)

            return final_message.content or "Sorry, I cannot process this request."

        else:
            # No tool call, return response directly
            self.llm_client.add_assistant_message(content=message.content)
            return message.content or "Sorry, I cannot understand your request."

    async def _execute_tool_call(self, tool_call: Any) -> str:
        """
        Execute tool call

        Args:
            tool_call: OpenAI tool call object

        Returns:
            Tool execution result (string format)
        """
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)

        # Display tool call information
        click.echo(f"🔧 Calling tool: {function_name}", err=True)
        click.echo(f"   Arguments: {json.dumps(function_args, ensure_ascii=False)}", err=True)

        try:
            # Call MCP tool
            result = await self.mcp_client.call_tool(function_name, function_args)

            # Format result
            formatted_result = self._format_tool_result(result)

            click.echo(f"✓ Tool execution successful", err=True)

            return formatted_result

        except Exception as e:
            error_msg = f"Tool call failed: {str(e)}"
            click.echo(f"✗ {error_msg}", err=True)
            return error_msg

    def _format_tool_result(self, result: Any) -> str:
        """
        Format tool return result

        Args:
            result: Tool return result

        Returns:
            Formatted string
        """
        # If result has content attribute
        if hasattr(result, 'content') and result.content:
            content_list = result.content
            if isinstance(content_list, list) and len(content_list) > 0:
                # Get first content item
                first_content = content_list[0]
                if hasattr(first_content, 'text'):
                    return first_content.text

        # Otherwise try direct conversion
        if isinstance(result, str):
            return result
        elif isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, indent=2)
        else:
            return str(result)

    def get_conversation_summary(self) -> str:
        """
        Get conversation summary

        Returns:
            Conversation summary information
        """
        message_count = self.llm_client.get_message_count()
        return f"Current conversation contains {message_count} messages"

    def clear_conversation(self) -> None:
        """Clear conversation history (keep system message)"""
        self.llm_client.clear_history()


async def create_chat_agent(
    server_script: Path,
    llm_api_key: Optional[str] = None,
    llm_api_base: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> ChatAgent:
    """
    Create and initialize chat agent

    Args:
        server_script: MCP server script path
        llm_api_key: LLM API key
        llm_api_base: LLM API endpoint
        system_prompt: System prompt

    Returns:
        Initialized ChatAgent instance
    """
    # Create MCP client (note: needs to be used within async with block)
    from mcp.client import mcp_client

    # Create LLM client
    llm_client = LLMClient(
        api_key=llm_api_key,
        api_base=llm_api_base,
    )

    # Note: This function should not directly return agent
    # Should be created in caller's async with block
    raise NotImplementedError(
        "Please use async with mcp_client(server_script) to create MCP client, "
        "then manually create ChatAgent"
    )

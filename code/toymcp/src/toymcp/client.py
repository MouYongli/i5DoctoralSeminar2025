"""
ToyMCP Client - Python Client API

Provides an easy-to-use Python API for connecting to and using MCP servers
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Resource, Tool, Prompt

logger = logging.getLogger(__name__)


class MCPClient:
    """MCP Client Wrapper"""

    def __init__(self, server_script: str | Path):
        """
        Initialize client

        Args:
            server_script: Server script path
        """
        self.server_script = str(server_script)
        self.session: Optional[ClientSession] = None
        self._read = None
        self._write = None
        self._client_context = None

    async def connect(self):
        """Connect to MCP server"""
        logger.info(f"Connecting to server: {self.server_script}")

        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script]
        )

        # Establish connection
        self._client_context = stdio_client(server_params)
        self._read, self._write = await self._client_context.__aenter__()

        # Create session
        self.session = ClientSession(self._read, self._write)
        await self.session.__aenter__()

        # Initialize
        await self.session.initialize()

        logger.info("Connection successful")

    async def disconnect(self):
        """Disconnect"""
        logger.info("Disconnecting")

        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
        except (RuntimeError, Exception) as e:
            # Suppress errors during cleanup, especially during shutdown
            logger.debug(f"Error during session cleanup: {e}")
            self.session = None

        try:
            if self._client_context:
                await self._client_context.__aexit__(None, None, None)
                self._client_context = None
        except (RuntimeError, Exception) as e:
            # Suppress errors during cleanup, especially during shutdown
            logger.debug(f"Error during client context cleanup: {e}")
            self._client_context = None

    def _ensure_connected(self):
        """Ensure connected to server"""
        if not self.session:
            raise RuntimeError("Not connected to server, please call connect() first")

    # ========================================
    # Resource operations
    # ========================================

    async def list_resources(self) -> List[Resource]:
        """
        List all resources

        Returns:
            Resource list
        """
        self._ensure_connected()
        result = await self.session.list_resources()
        return result.resources

    async def read_resource(self, uri: str) -> str:
        """
        Read resource content

        Args:
            uri: Resource URI

        Returns:
            Resource content
        """
        self._ensure_connected()
        result = await self.session.read_resource(uri)

        # Extract text content
        if result.contents:
            return result.contents[0].text
        return ""

    # ========================================
    # Tool operations
    # ========================================

    async def list_tools(self) -> List[Tool]:
        """
        List all tools

        Returns:
            Tool list
        """
        self._ensure_connected()
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: Dict[str, Any]):
        """
        Call a tool

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        self._ensure_connected()
        result = await self.session.call_tool(name, arguments)
        return result

    # ========================================
    # Prompt operations
    # ========================================

    async def list_prompts(self) -> List[Prompt]:
        """
        List all prompts

        Returns:
            Prompt list
        """
        self._ensure_connected()
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(self, name: str, arguments: Dict[str, Any] = None) -> str:
        """
        Get prompt content

        Args:
            name: Prompt name
            arguments: Prompt arguments

        Returns:
            Prompt text
        """
        self._ensure_connected()
        result = await self.session.get_prompt(name, arguments or {})

        # Extract prompt text
        if result.messages:
            return result.messages[0].content.text
        return ""

    # ========================================
    # Convenience methods
    # ========================================

    async def create_file(self, filename: str, content: str) -> str:
        """
        Create file (convenience method)

        Args:
            filename: Filename
            content: File content

        Returns:
            Execution result
        """
        return await self.call_tool("create_file", {
            "filename": filename,
            "content": content
        })

    async def read_file(self, filename: str) -> str:
        """
        Read file (convenience method)

        Args:
            filename: Filename

        Returns:
            File content
        """
        return await self.call_tool("read_file", {"filename": filename})

    async def delete_file(self, filename: str) -> str:
        """
        Delete file (convenience method)

        Args:
            filename: Filename

        Returns:
            Execution result
        """
        return await self.call_tool("delete_file", {"filename": filename})

    async def list_files(self) -> str:
        """
        List files (convenience method)

        Returns:
            File list
        """
        return await self.call_tool("list_files", {})

    async def calculate(self, operation: str, a: float, b: float = None) -> str:
        """
        Perform calculation (convenience method)

        Args:
            operation: Operation type (add, subtract, multiply, divide, power, sqrt)
            a: First operand
            b: Second operand (not needed for sqrt)

        Returns:
            Calculation result
        """
        args = {"operation": operation, "a": a}
        if b is not None:
            args["b"] = b

        return await self.call_tool("calculate", args)


@asynccontextmanager
async def mcp_client(server_script: str | Path):
    """
    Context manager: Automatic connection and disconnection

    Args:
        server_script: Server script path

    Yields:
        MCPClient instance

    Example:
        ```python
        async with mcp_client("server.py") as client:
            result = await client.calculate("add", 5, 3)
            print(result)
        ```
    """
    client = MCPClient(server_script)
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()


# ========================================
# Example usage
# ========================================

async def example_usage():
    """Example: How to use the client"""

    # Server script path
    server_script = Path(__file__).parent / "server.py"

    # Use context manager
    async with mcp_client(server_script) as client:
        # List tools
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Create file
        result = await client.create_file("test.txt", "Hello, MCP!")
        print(result)

        # Read file
        content = await client.read_file("test.txt")
        print(f"File content: {content}")

        # Perform calculation
        calc_result = await client.calculate("add", 5, 3)
        print(f"5 + 3 = {calc_result}")

        # List resources
        resources = await client.list_resources()
        print(f"Available resources: {[r.name for r in resources]}")

        # Get prompt
        prompt = await client.get_prompt("code_review", {"language": "Python"})
        print(f"Prompt: {prompt[:100]}...")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run example
    asyncio.run(example_usage())

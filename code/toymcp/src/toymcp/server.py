"""
ToyMCP Server - Complete MCP Server Implementation

This is a fully functional MCP server that integrates:
- Resources: File system access
- Tools: File operations and calculator
- Prompts: Development assistant templates
"""

import asyncio
import logging
import sys
import math
from pathlib import Path
from datetime import datetime
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    Prompt,
    PromptArgument,
    TextContent,
    GetPromptResult,
    PromptMessage,
)

logger = logging.getLogger(__name__)


class ToyMCPServer:
    """ToyMCP Server Class"""

    def __init__(self, work_dir: Optional[Path] = None):
        """
        Initialize server

        Args:
            work_dir: Working directory path, defaults to workspace subdirectory of current directory
        """
        self.app = Server("toymcp-server")
        self.work_dir = work_dir or Path.cwd() / "workspace"
        self.work_dir.mkdir(exist_ok=True)

        # Register all handlers
        self._register_handlers()

        # Initialize workspace
        self._init_workspace()

        logger.info(f"Server initialized, working directory: {self.work_dir}")

    def _init_workspace(self):
        """Initialize workspace and create welcome file"""
        welcome_file = self.work_dir / "welcome.txt"
        if not welcome_file.exists():
            welcome_file.write_text(
                f"Welcome to ToyMCP!\n\n"
                f"This is a project for learning Model Context Protocol.\n"
                f"Created at: {datetime.now().isoformat()}\n"
            )
            logger.info("Welcome file created")

    def _register_handlers(self):
        """Register all MCP handlers"""

        # Resource handlers
        @self.app.list_resources()
        async def list_resources() -> list[Resource]:
            return await self._list_resources()

        @self.app.read_resource()
        async def read_resource(uri: str) -> str:
            return await self._read_resource(uri)

        # Tool handlers
        @self.app.list_tools()
        async def list_tools() -> list[Tool]:
            return await self._list_tools()

        @self.app.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            return await self._call_tool(name, arguments)

        # Prompt handlers
        @self.app.list_prompts()
        async def list_prompts() -> list[Prompt]:
            return await self._list_prompts()

        @self.app.get_prompt()
        async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
            return await self._get_prompt(name, arguments)

    # ========================================
    # Resource functionality
    # ========================================

    async def _list_resources(self) -> list[Resource]:
        """List all text file resources"""
        logger.debug("Listing resources")

        resources = []
        for file_path in self.work_dir.glob("*.txt"):
            stat = file_path.stat()
            size = stat.st_size
            modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

            resources.append(Resource(
                uri=f"file:///{file_path.name}",
                name=file_path.name,
                description=f"Text file ({size} bytes, modified at {modified})",
                mimeType="text/plain"
            ))

        logger.debug(f"Found {len(resources)} resources")
        return resources

    async def _read_resource(self, uri: str) -> str:
        """Read resource content"""
        logger.debug(f"Reading resource: {uri}")

        filename = uri.replace("file:///", "")
        file_path = self.work_dir / filename

        # Security check
        file_path = file_path.resolve()
        if not file_path.is_relative_to(self.work_dir.resolve()):
            raise ValueError(f"Access denied to file outside directory: {filename}")

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filename}")

        content = file_path.read_text(encoding="utf-8")
        logger.debug(f"Successfully read {len(content)} characters")
        return content

    # ========================================
    # Tool functionality
    # ========================================

    async def _list_tools(self) -> list[Tool]:
        """List all tools"""
        return [
            # File operation tools
            Tool(
                name="create_file",
                description="Create a new text file in the working directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename (must end with .txt)"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content"
                        }
                    },
                    "required": ["filename", "content"]
                }
            ),
            Tool(
                name="read_file",
                description="Read a file from the working directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename"
                        }
                    },
                    "required": ["filename"]
                }
            ),
            Tool(
                name="delete_file",
                description="Delete a file from the working directory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": "string",
                            "description": "Filename to delete"
                        }
                    },
                    "required": ["filename"]
                }
            ),
            Tool(
                name="list_files",
                description="List all files in the working directory",
                inputSchema={
                    "type": "object",
                    "properties": {}
                }
            ),

            # Calculator tool
            Tool(
                name="calculate",
                description="Perform mathematical calculations",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide", "power", "sqrt"],
                            "description": "Operation type"
                        },
                        "a": {
                            "type": "number",
                            "description": "First operand (radicand for sqrt)"
                        },
                        "b": {
                            "type": "number",
                            "description": "Second operand (not needed for sqrt)"
                        }
                    },
                    "required": ["operation", "a"]
                }
            ),
        ]

    async def _call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        """Call a tool"""
        logger.debug(f"Calling tool: {name}, arguments: {arguments}")

        try:
            # File operation tools
            if name == "create_file":
                return await self._create_file(arguments)
            elif name == "read_file":
                return await self._read_file(arguments)
            elif name == "delete_file":
                return await self._delete_file(arguments)
            elif name == "list_files":
                return await self._list_files_tool()

            # Calculator tool
            elif name == "calculate":
                return await self._calculate(arguments)

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def _create_file(self, arguments: dict) -> list[TextContent]:
        """Create file tool"""
        filename = arguments["filename"]
        content = arguments["content"]

        if not filename.endswith(".txt"):
            return [TextContent(type="text", text="Error: Filename must end with .txt")]

        file_path = self.work_dir / filename

        if file_path.exists():
            return [TextContent(type="text", text=f"Error: File already exists: {filename}")]

        file_path.write_text(content, encoding="utf-8")
        logger.info(f"Created file: {file_path}")

        return [TextContent(
            type="text",
            text=f"Successfully created file: {filename} ({len(content)} characters)"
        )]

    async def _read_file(self, arguments: dict) -> list[TextContent]:
        """Read file tool"""
        filename = arguments["filename"]
        file_path = self.work_dir / filename

        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File not found: {filename}")]

        content = file_path.read_text(encoding="utf-8")
        return [TextContent(type="text", text=content)]

    async def _delete_file(self, arguments: dict) -> list[TextContent]:
        """Delete file tool"""
        filename = arguments["filename"]
        file_path = self.work_dir / filename

        if not file_path.exists():
            return [TextContent(type="text", text=f"Error: File not found: {filename}")]

        file_path.unlink()
        logger.info(f"Deleted file: {file_path}")

        return [TextContent(type="text", text=f"Successfully deleted file: {filename}")]

    async def _list_files_tool(self) -> list[TextContent]:
        """List files tool"""
        files = list(self.work_dir.glob("*"))
        if not files:
            return [TextContent(type="text", text="Working directory is empty")]

        file_list = []
        for f in sorted(files):
            size = f.stat().st_size
            file_type = "directory" if f.is_dir() else "file"
            file_list.append(f"{f.name} ({file_type}, {size} bytes)")

        return [TextContent(
            type="text",
            text="File list:\n" + "\n".join(f"- {f}" for f in file_list)
        )]

    async def _calculate(self, arguments: dict) -> list[TextContent]:
        """Calculator tool"""
        operation = arguments["operation"]
        a = arguments["a"]
        b = arguments.get("b")

        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return [TextContent(type="text", text="Error: Cannot divide by zero")]
            result = a / b
        elif operation == "power":
            result = a ** b
        elif operation == "sqrt":
            if a < 0:
                return [TextContent(type="text", text="Error: Cannot take square root of negative number")]
            result = math.sqrt(a)
        else:
            return [TextContent(type="text", text=f"Error: Unknown operation: {operation}")]

        return [TextContent(type="text", text=f"Calculation result: {result}")]

    # ========================================
    # Prompt functionality
    # ========================================

    async def _list_prompts(self) -> list[Prompt]:
        """List all prompts"""
        return [
            Prompt(
                name="code_review",
                description="Code review assistant: Provide code quality analysis and improvement suggestions",
                arguments=[
                    PromptArgument(
                        name="language",
                        description="Programming language",
                        required=True
                    )
                ]
            ),
            Prompt(
                name="debug_help",
                description="Debugging assistant: Help analyze and resolve code errors",
                arguments=[]
            ),
        ]

    async def _get_prompt(self, name: str, arguments: dict) -> GetPromptResult:
        """Get prompt"""
        logger.debug(f"Getting prompt: {name}")

        if name == "code_review":
            language = arguments.get("language", "code")
            prompt_text = f"""Please review the following {language} code and provide detailed feedback.

Review points:
1. Code quality and readability
2. Potential bugs and issues
3. Performance optimization opportunities
4. Best practice recommendations
5. Security considerations

Please paste the code to review:
"""

            return GetPromptResult(
                description=f"{language} code review",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt_text)
                    )
                ]
            )

        elif name == "debug_help":
            prompt_text = """I encountered a code error and need help debugging.

Please provide:
1. Error cause analysis
2. Possible solutions
3. How to avoid similar issues
4. Debugging tips

Please paste the error message and related code:
"""

            return GetPromptResult(
                description="Debugging assistant",
                messages=[
                    PromptMessage(
                        role="user",
                        content=TextContent(type="text", text=prompt_text)
                    )
                ]
            )

        else:
            raise ValueError(f"Unknown prompt: {name}")

    # ========================================
    # Run server
    # ========================================

    async def run(self):
        """Run server (STDIO mode)"""
        logger.info("Starting ToyMCP server (STDIO mode)...")
        logger.info(f"Working directory: {self.work_dir.resolve()}")

        async with stdio_server() as (read_stream, write_stream):
            await self.app.run(
                read_stream,
                write_stream,
                self.app.create_initialization_options()
            )


def create_server(work_dir: Optional[Path] = None) -> ToyMCPServer:
    """
    Create server instance

    Args:
        work_dir: Working directory path

    Returns:
        ToyMCPServer instance
    """
    return ToyMCPServer(work_dir=work_dir)


async def main():
    """Main function: Run server"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Create and run server
    server = create_server()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

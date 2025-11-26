#!/usr/bin/env python3
"""
Full-featured MCP server example

This server combines resources, tools, and prompts into one example to
demonstrate how to expose multiple capabilities from a single MCP server.

Features:
- Resources: access text files in the filesystem
- Tools: file operations (create/read/delete) and a calculator
- Prompts: code review and documentation generation templates

Run:
    python full_featured_server.py

Usage:
    Configure in Claude Desktop to use all capabilities.
"""

import asyncio
import logging
import sys
import math
from pathlib import Path
from datetime import datetime
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Create server
app = Server("full-featured-mcp-server")

# Working directory
WORK_DIR = Path(__file__).parent / "workspace"
WORK_DIR.mkdir(exist_ok=True)

# Create sample file
if not list(WORK_DIR.glob("*.txt")):
    (WORK_DIR / "welcome.txt").write_text(
        f"Welcome to the MCP server!\nCreated at: {datetime.now().isoformat()}"
    )
    logger.info(f"Workspace created: {WORK_DIR}")

# ========================================
# Resource functionality
# ========================================

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all text files in the workspace"""
    logger.info("Listing resources")

    resources = []
    for file_path in WORK_DIR.glob("*.txt"):
        # Get file info
        stat = file_path.stat()
        size = stat.st_size
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()

        resources.append(Resource(
            uri=f"file:///{file_path.name}",
            name=file_path.name,
            description=f"Text file ({size} bytes, modified at {modified})",
            mimeType="text/plain"
        ))

    logger.info(f"Found {len(resources)} resources")
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read file contents"""
    logger.info(f"Reading resource: {uri}")

    filename = uri.replace("file:///", "")
    file_path = WORK_DIR / filename

    # Safety check
    try:
        file_path = file_path.resolve()
        if not file_path.is_relative_to(WORK_DIR.resolve()):
            raise ValueError(f"Access to files outside workspace denied: {filename}")
    except ValueError as e:
        logger.error(f"Safety check failed: {e}")
        raise

    if not file_path.exists():
        logger.error(f"File not found: {filename}")
        raise FileNotFoundError(f"File not found: {filename}")

    content = file_path.read_text(encoding="utf-8")
    logger.info(f"Read {len(content)} characters")
    return content

# ========================================
# Tool functionality
# ========================================

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    logger.info("Listing tools")

    return [
        # File operation tools
        Tool(
            name="create_file",
            description="Create a new text file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File name (must end with .txt)"
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
            name="delete_file",
            description="Delete a file in the workspace",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "File name to delete"
                    }
                },
                "required": ["filename"]
            }
        ),
        Tool(
            name="list_files",
            description="List all files in the workspace",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Calculator tool
        Tool(
            name="calculate",
            description="Perform math operations",
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

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool"""
    logger.info(f"Calling tool: {name}, args: {arguments}")

    try:
        # File operation tools
        if name == "create_file":
            filename = arguments["filename"]
            content = arguments["content"]

            # Validate filename
            if not filename.endswith(".txt"):
                return [TextContent(
                    type="text",
                    text="Error: filename must end with .txt"
                )]

            file_path = WORK_DIR / filename

            # Check if file exists
            if file_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: file already exists: {filename}"
                )]

            # Create file
            file_path.write_text(content, encoding="utf-8")
            logger.info(f"Created file: {file_path}")

            return [TextContent(
                type="text",
                text=f"Created file: {filename} ({len(content)} characters)"
            )]

        elif name == "delete_file":
            filename = arguments["filename"]
            file_path = WORK_DIR / filename

            if not file_path.exists():
                return [TextContent(
                    type="text",
                    text=f"Error: file not found: {filename}"
                )]

            file_path.unlink()
            logger.info(f"Deleted file: {file_path}")

            return [TextContent(
                type="text",
                text=f"Deleted file: {filename}"
            )]

        elif name == "list_files":
            files = list(WORK_DIR.glob("*"))
            if not files:
                return [TextContent(
                    type="text",
                    text="Workspace is empty"
                )]

            file_list = []
            for f in sorted(files):
                size = f.stat().st_size
                file_list.append(f"{f.name} ({size} bytes)")

            return [TextContent(
                type="text",
                text="File list:\n" + "\n".join(f"- {f}" for f in file_list)
            )]

        # Calculator tool
        elif name == "calculate":
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
                    return [TextContent(type="text", text="Error: divisor cannot be 0")]
                result = a / b
            elif operation == "power":
                result = a ** b
            elif operation == "sqrt":
                if a < 0:
                    return [TextContent(type="text", text="Error: cannot take square root of negative number")]
                result = math.sqrt(a)
            else:
                return [TextContent(type="text", text=f"Error: unknown operation: {operation}")]

            return [TextContent(
                type="text",
                text=f"Result: {result}"
            )]

        else:
            raise ValueError(f"Unknown tool: {name}")

    except KeyError as e:
        logger.error(f"Missing argument: {e}")
        return [TextContent(type="text", text=f"Error: missing required argument {e}")]
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        return [TextContent(type="text", text=f"Error: {str(e)}")]

# ========================================
# Prompt functionality
# ========================================

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all prompts"""
    logger.info("Listing prompts")

    return [
        Prompt(
            name="code_review",
            description="Code review helper",
            arguments=[
                PromptArgument(name="language", description="Programming language", required=True)
            ]
        ),
        Prompt(
            name="generate_docs",
            description="Documentation helper",
            arguments=[
                PromptArgument(name="doc_type", description="Documentation type", required=True)
            ]
        ),
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Return prompt template"""
    logger.info(f"Get prompt: {name}, args: {arguments}")

    if name == "code_review":
        language = arguments.get("language", "code")

        prompt_text = f"""Please review the following {language} code and provide feedback.

Focus on:
1. Code quality and readability
2. Potential bugs and issues
3. Performance optimization opportunities
4. Best practice recommendations

Please paste the code:
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

    elif name == "generate_docs":
        doc_type = arguments.get("doc_type", "API")

        prompt_text = f"""Please generate {doc_type} documentation.

The documentation should be clear, complete, and easy to understand.

Please provide the content that needs to be documented:
"""

        return GetPromptResult(
            description=f"{doc_type} documentation generation",
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

async def main():
    """Run the server"""
    logger.info("=" * 50)
    logger.info("Starting full-featured MCP server")
    logger.info(f"Workspace: {WORK_DIR.resolve()}")
    logger.info("=" * 50)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

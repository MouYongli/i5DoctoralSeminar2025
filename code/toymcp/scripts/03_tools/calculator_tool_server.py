#!/usr/bin/env python3
"""
Calculator tool server example

This server exposes basic math tools to demonstrate:
1. How to define tools and their input schema
2. How to handle tool invocations
3. How to perform error handling
4. How to return execution results

Run:
    python calculator_tool_server.py

Usage:
    Configure in Claude Desktop, then ask it to compute math,
    e.g. "Please calculate 15 + 27"
"""

import asyncio
import logging
import sys
import math
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Create server
app = Server("calculator-tool-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available calculator tools"""
    logger.info("Listing tools")

    return [
        Tool(
            name="add",
            description="Addition: sum of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="subtract",
            description="Subtraction: difference of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Minuend"
                    },
                    "b": {
                        "type": "number",
                        "description": "Subtrahend"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description="Multiplication: product of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="divide",
            description="Division: quotient of two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Dividend"
                    },
                    "b": {
                        "type": "number",
                        "description": "Divisor (cannot be 0)"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="power",
            description="Exponentiation: compute a to the power of b",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Base"
                    },
                    "b": {
                        "type": "number",
                        "description": "Exponent"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="sqrt",
            description="Square root: compute sqrt(x)",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {
                        "type": "number",
                        "description": "Radicand (must be ≥ 0)"
                    }
                },
                "required": ["x"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a calculator tool"""
    logger.info(f"Calling tool: {name}, args: {arguments}")

    try:
        if name == "add":
            result = arguments["a"] + arguments["b"]

        elif name == "subtract":
            result = arguments["a"] - arguments["b"]

        elif name == "multiply":
            result = arguments["a"] * arguments["b"]

        elif name == "divide":
            if arguments["b"] == 0:
                logger.warning("Divisor is 0")
                return [TextContent(
                    type="text",
                    text="Error: divisor cannot be 0"
                )]
            result = arguments["a"] / arguments["b"]

        elif name == "power":
            result = arguments["a"] ** arguments["b"]

        elif name == "sqrt":
            if arguments["x"] < 0:
                logger.warning("Square root of negative number requested")
                return [TextContent(
                    type="text",
                    text="Error: cannot take square root of a negative number"
                )]
            result = math.sqrt(arguments["x"])

        else:
            logger.error(f"Unknown tool: {name}")
            raise ValueError(f"Unknown tool: {name}")

        logger.info(f"Calculation result: {result}")
        return [TextContent(type="text", text=str(result))]

    except KeyError as e:
        logger.error(f"Missing required argument: {e}")
        return [TextContent(
            type="text",
            text=f"Error: missing required argument {e}"
        )]
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"Execution error: {str(e)}"
        )]

async def main():
    """Run the server"""
    logger.info("Starting calculator tool server...")

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

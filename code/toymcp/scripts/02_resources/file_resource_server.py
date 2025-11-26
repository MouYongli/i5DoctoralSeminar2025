#!/usr/bin/env python3
"""
File Resource Server Example

This server exposes text files in a directory as resources, demonstrating:
1. How to list resources
2. How to read resource contents
3. How to perform security checks (to prevent directory traversal)

How to run:
    python file_resource_server.py

Usage:
    Configure in Claude Desktop so Claude can access files under the data/ directory
"""

import asyncio
import logging
import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Create server
app = Server("file-resource-server")

# Working directory: stores accessible files
RESOURCE_DIR = Path(__file__).parent / "data"

# Ensure the directory exists
RESOURCE_DIR.mkdir(exist_ok=True)

# Create some sample files
if not list(RESOURCE_DIR.glob("*.txt")):
    (RESOURCE_DIR / "example1.txt").write_text("This is the first sample file.\nContains some text content.")
    (RESOURCE_DIR / "example2.txt").write_text("This is the second sample file.\nDemonstrates multiple resources.")
    logger.info(f"Sample files created in {RESOURCE_DIR}")

@app.list_resources()
async def list_resources() -> list[Resource]:
    """List all available text file resources"""
    logger.info("Listing resources")

    resources = []
    for file_path in RESOURCE_DIR.glob("*.txt"):
        resources.append(Resource(
            uri=f"file:///{file_path.name}",
            name=file_path.name,
            description=f"Text file: {file_path.name}",
            mimeType="text/plain"
        ))

    logger.info(f"Found {len(resources)} resources")
    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read the content of the specified resource"""
    logger.info(f"Reading resource: {uri}")

    # Extract the filename from the URI
    # Convert AnyUrl to string if needed
    uri_str = str(uri)
    filename = uri_str.replace("file:///", "")
    file_path = RESOURCE_DIR / filename

    # Security check: ensure the file is within the working directory
    try:
        file_path = file_path.resolve()
        if not file_path.is_relative_to(RESOURCE_DIR.resolve()):
            raise ValueError(f"Access denied for file outside directory: {filename}")
    except ValueError as e:
        logger.error(f"Security check failed: {e}")
        raise

    # Check if file exists
    if not file_path.exists():
        logger.error(f"File does not exist: {filename}")
        raise FileNotFoundError(f"File does not exist: {filename}")

    # Read and return content
    content = file_path.read_text(encoding="utf-8")
    logger.info(f"Successfully read {len(content)} characters")
    return content

async def main():
    """Run the server"""
    logger.info("Starting file resource server...")
    logger.info(f"Resource directory: {RESOURCE_DIR.resolve()}")

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
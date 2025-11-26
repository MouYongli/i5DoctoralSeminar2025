#!/usr/bin/env python3
"""
Basic MCP server example.

This server has no resources, tools, or prompts - it only responds to client
initialization requests. Used for learning basic MCP communication flow.
"""

import asyncio
import json
import logging
import sys
from pathlib import Path
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure log directory
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging to stderr and file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_DIR / "server.log", mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Create logger for JSON-RPC messages
message_logger = logging.getLogger("jsonrpc")
message_handler = logging.FileHandler(LOG_DIR / "messages.log", mode='a', encoding='utf-8')
message_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
message_logger.addHandler(message_handler)
message_logger.setLevel(logging.DEBUG)

# Create MCP server instance
app = Server("basic-stdio-server")

async def log_messages(read_stream, write_stream):
    """Intercept and log all JSON-RPC messages"""
    import anyio

    # Create new streams for passing to app
    app_read_writer, app_read_stream = anyio.create_memory_object_stream(0)
    app_write_stream, app_write_reader = anyio.create_memory_object_stream(0)

    async def read_interceptor():
        """Intercept read messages (requests from client)"""
        async with app_read_writer:
            async for message in read_stream:
                # Log received messages
                try:
                    # Extract JSON-RPC message from SessionMessage
                    if hasattr(message, 'message') and hasattr(message.message, 'root'):
                        jsonrpc_msg = message.message.root
                        msg_dict = jsonrpc_msg.model_dump() if hasattr(jsonrpc_msg, 'model_dump') else vars(jsonrpc_msg)
                    elif hasattr(message, 'model_dump'):
                        msg_dict = message.model_dump()
                    else:
                        msg_dict = {"raw": str(message)}

                    msg_json = json.dumps(msg_dict, indent=2, ensure_ascii=False)
                    message_logger.info(f"\n{'='*80}\n[SERVER] RECEIVED FROM CLIENT:\n{msg_json}\n{'='*80}")
                except Exception as e:
                    message_logger.error(f"Failed to log message: {e}")
                await app_read_writer.send(message)

    async def write_interceptor():
        """Intercept write messages (responses sent to client)"""
        async with app_write_reader:
            async for message in app_write_reader:
                # Log sent messages
                try:
                    # Extract JSON-RPC message from SessionMessage
                    if hasattr(message, 'message') and hasattr(message.message, 'root'):
                        jsonrpc_msg = message.message.root
                        msg_dict = jsonrpc_msg.model_dump() if hasattr(jsonrpc_msg, 'model_dump') else vars(jsonrpc_msg)
                    elif hasattr(message, 'model_dump'):
                        msg_dict = message.model_dump()
                    else:
                        msg_dict = {"raw": str(message)}

                    msg_json = json.dumps(msg_dict, indent=2, ensure_ascii=False)
                    message_logger.info(f"\n{'='*80}\n[SERVER] SENT TO CLIENT:\n{msg_json}\n{'='*80}")
                except Exception as e:
                    message_logger.error(f"Failed to log message: {e}")
                await write_stream.send(message)

    async with anyio.create_task_group() as tg:
        tg.start_soon(read_interceptor)
        tg.start_soon(write_interceptor)

        try:
            # Run server
            await app.run(
                app_read_stream,
                app_write_stream,
                app.create_initialization_options()
            )
        finally:
            # Cancel interceptor tasks when server stops
            tg.cancel_scope.cancel()

async def main():
    """Run server"""
    logger.info("Starting MCP server...")
    logger.info(f"Log files location: {LOG_DIR.absolute()}")

    # Use stdio_server context manager
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Server ready, waiting for client connection...")

        # Use message interceptor
        await log_messages(read_stream, write_stream)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

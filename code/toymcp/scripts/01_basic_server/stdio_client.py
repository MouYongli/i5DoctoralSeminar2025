#!/usr/bin/env python3
"""
Simple client for testing STDIO MCP server.

This client connects to stdio_server.py and performs basic initialization tests.

Usage:
    uv run python stdio_client.py
"""

import asyncio
import json
import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure log directory
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "client.log", mode='a', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Create logger for JSON-RPC messages
message_logger = logging.getLogger("jsonrpc.client")
message_handler = logging.FileHandler(LOG_DIR / "messages.log", mode='a', encoding='utf-8')
message_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
message_logger.addHandler(message_handler)
message_logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def log_client_messages(read_stream, write_stream):
    """Intercept and log all JSON-RPC messages from client"""
    import anyio

    # Create new streams for passing to session
    session_read_writer, session_read_stream = anyio.create_memory_object_stream(0)
    session_write_stream, session_write_reader = anyio.create_memory_object_stream(0)

    async def read_interceptor():
        """Intercept read messages (responses from server)"""
        async with session_read_writer:
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
                    message_logger.info(f"\n{'='*80}\n[CLIENT] RECEIVED FROM SERVER:\n{msg_json}\n{'='*80}")
                except Exception as e:
                    message_logger.error(f"Failed to log message: {e}")
                await session_read_writer.send(message)

    async def write_interceptor():
        """Intercept write messages (requests sent to server)"""
        async with session_write_reader:
            async for message in session_write_reader:
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
                    message_logger.info(f"\n{'='*80}\n[CLIENT] SENT TO SERVER:\n{msg_json}\n{'='*80}")
                except Exception as e:
                    message_logger.error(f"Failed to log message: {e}")
                await write_stream.send(message)

    async with anyio.create_task_group() as tg:
        tg.start_soon(read_interceptor)
        tg.start_soon(write_interceptor)

        try:
            # Create session
            async with ClientSession(session_read_stream, session_write_stream) as session:
                yield session
        finally:
            # Cancel interceptor tasks when session ends
            tg.cancel_scope.cancel()

async def main():
    """Test server connection"""
    # Server script path
    server_script = Path(__file__).parent / "stdio_server.py"

    print(f"Connecting to server: {server_script}")
    print(f"Log files location: {LOG_DIR.absolute()}")
    logger.info("Client starting")

    # Configure server parameters
    server_params = StdioServerParameters(
        command="python",
        args=[str(server_script)]
    )

    try:
        # Connect to server
        async with stdio_client(server_params) as (read, write):
            print("Connection established")
            logger.info("Connected to server")

            # Create session with message interceptor
            async with log_client_messages(read, write) as session:
                print("Session created")
                logger.info("Session created")

                # Initialize
                init_result = await session.initialize()
                print("Initialization complete")
                logger.info("Initialization complete")

                print("\nServer information:", flush=True)
                print(f"  Protocol version: {init_result.protocolVersion}", flush=True)
                print(f"  Server name: {init_result.serverInfo.name}", flush=True)
                print(f"  Server version: {init_result.serverInfo.version}", flush=True)

                # This basic server has no functionality, so we only test the connection
                print("\nTest successful! Server is running normally.", flush=True)
                logger.info("Test complete")

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

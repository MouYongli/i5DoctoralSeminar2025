#!/usr/bin/env python3
"""
Example MCP server using SSE transport

This server exposes MCP over HTTP via Server-Sent Events (SSE).
It demonstrates how to build an HTTP-based MCP server with FastAPI.

Run:
    python sse_server.py
    or
    uvicorn sse_server:app --host 0.0.0.0 --port 8000

Access:
    SSE endpoint: http://localhost:8000/sse
    Message endpoint: http://localhost:8000/message
    Health check: http://localhost:8000/health

Note:
    Required deps: pip install fastapi uvicorn sse-starlette
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MCP SSE Server",
    description="MCP server example using Server-Sent Events",
    version="1.0.0"
)

# Configure CORS (allow any origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track active connections
active_connections: set[int] = set()

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("MCP SSE server started")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info(f"Server shutting down, active connections: {len(active_connections)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MCP SSE Server",
        "version": "1.0.0",
        "endpoints": {
            "sse": "/sse",
            "message": "/message",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(active_connections)
    }

@app.get("/sse")
async def sse_endpoint(request: Request):
    """
    SSE connection endpoint

    Clients connect here to receive server-pushed messages via SSE.
    """
    connection_id = id(request)
    logger.info(f"New SSE connection: {connection_id}")

    async def event_stream() -> AsyncIterator[str]:
        """Generate SSE event stream"""
        active_connections.add(connection_id)

        try:
            # Send connected event
            yield f"event: connected\n"
            yield f"data: {{'connection_id': {connection_id}}}\n\n"

            # Keep connection alive (heartbeat)
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info(f"Client disconnected: {connection_id}")
                    break

                # Send heartbeat
                yield f"event: heartbeat\n"
                yield f"data: {{'timestamp': '{datetime.now().isoformat()}'}}\n\n"

                await asyncio.sleep(30)  # Send heartbeat every 30 seconds

        except asyncio.CancelledError:
            logger.info(f"Connection cancelled: {connection_id}")
        except Exception as e:
            logger.error(f"SSE error: {e}", exc_info=True)
        finally:
            active_connections.discard(connection_id)
            logger.info(f"Connection closed: {connection_id}, remaining: {len(active_connections)}")

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        }
    )

@app.post("/message")
async def handle_message(request: Request):
    """
    Handle JSON-RPC messages from clients

    This is a simplified example. Real applications need full MCP message handling.
    """
    try:
        body = await request.json()
        logger.info(f"Received message: {body}")

        # Extract JSON-RPC fields
        method = body.get("method")
        msg_id = body.get("id")
        params = body.get("params", {})

        # Simplified handling (should use MCP SDK in real use)
        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "mcp-sse-server",
                        "version": "1.0.0"
                    }
                }
            }

        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "tools": [
                        {
                            "name": "echo",
                            "description": "Echo a message",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                },
                                "required": ["message"]
                            }
                        }
                    ]
                }
            }

        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})

            if tool_name == "echo":
                result_text = f"Echo: {arguments.get('message', '')}"
            else:
                result_text = f"Unknown tool: {tool_name}"

            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": result_text
                        }
                    ]
                }
            }

        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }

        logger.info(f"Sending response: {response}")
        return JSONResponse(content=response)

    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "jsonrpc": "2.0",
                "id": body.get("id") if "body" in locals() else None,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }
        )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )

def main():
    """Run the server"""
    logger.info("Starting MCP SSE server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

if __name__ == "__main__":
    main()

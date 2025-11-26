# SSE Transport

## What Is SSE Transport?

SSE (Server-Sent Events) is an MCP transport over HTTP suited for remote communication.

### STDIO vs SSE

| Feature | STDIO | SSE |
|------|-------|-----|
| Transport | stdin/stdout | HTTP |
| Typical use | Local process | Remote server |
| Deployment | Simple (local command) | Requires web server |
| Firewalls | N/A | Friendly (standard HTTP) |
| Scalability | Single machine | Distributed |

### How SSE Works

```
┌──────────────┐                    ┌──────────────┐
│              │   HTTP POST        │              │
│  MCP Client  │──────────────────>│  MCP Server  │
│              │   (JSON-RPC req)   │   (HTTP)     │
│              │                    │              │
│              │   SSE Stream       │              │
│              │<──────────────────│              │
│              │   (JSON-RPC res)   │              │
└──────────────┘                    └──────────────┘
```

1) Client sends JSON-RPC over HTTP POST  
2) Server responds via SSE stream  
3) Long-lived connection allows server push  

## SSE Basics

### Server-Sent Events

SSE streams data from server to client:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: message
data: {"jsonrpc": "2.0", "id": 1, "result": {...}}

event: message
data: {"jsonrpc": "2.0", "id": 2, "result": {...}}
```

### Key Properties

- **One-way stream**: server → client  
- **Auto-reconnect**: clients reconnect on drop  
- **Event types**: named events supported  
- **Text payloads**: typically JSON  

## Building an SSE MCP Server

### Using FastAPI

FastAPI has native SSE support and works well for MCP SSE servers.

### Skeleton

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
from mcp.server import Server
from mcp.server.sse import SseServerTransport

app = FastAPI()
mcp_server = Server("sse-mcp-server")

@app.post("/sse")
async def handle_sse(request: Request):
    # Create SSE transport
    sse = SseServerTransport("/messages")

    # Process MCP messages
    async with sse:
        await mcp_server.run(
            sse.read_stream,
            sse.write_stream,
            mcp_server.create_initialization_options()
        )
```

### Full Example

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import uvicorn
import json
from typing import AsyncIterator
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create FastAPI app
app = FastAPI(title="MCP SSE Server")

# Create MCP server
mcp_server = Server("calculator-sse")

# Define tool
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@mcp_server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(result))]
    raise ValueError(f"Unknown tool: {name}")

# SSE endpoint
@app.get("/sse")
async def sse_endpoint(request: Request):
    """SSE connection endpoint"""

    async def event_stream() -> AsyncIterator[str]:
        # Example SSE stream; real version should forward MCP responses
        try:
            while True:
                if await request.is_disconnected():
                    break

                yield f"data: {json.dumps({'status': 'connected'})}\n\n"

                await asyncio.sleep(30)  # heartbeat

        except asyncio.CancelledError:
            pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )

# Message endpoint
@app.post("/message")
async def handle_message(request: Request):
    """Handle JSON-RPC requests from clients"""
    body = await request.json()

    # Forward to MCP server in a real implementation
    return {"jsonrpc": "2.0", "id": body.get("id"), "result": {}}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Full Code

See [scripts/05_sse_server/sse_server.py](../scripts/05_sse_server/sse_server.py).

## Running the SSE Server

### Install dependencies

```bash
pip install fastapi uvicorn sse-starlette
```

### Start the server

```bash
# Option 1: direct run
python scripts/05_sse_server/sse_server.py

# Option 2: uvicorn
uvicorn sse_server:app --host 0.0.0.0 --port 8000 --reload
```

### Test the connection

```bash
# Test SSE
curl -N http://localhost:8000/sse

# Send JSON-RPC request
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Using the included `sse_server.py` demo

Endpoints:
- `GET /sse` — connect to the SSE stream; you’ll receive a `connected` event and periodic `heartbeat` events.
- `POST /message` — send JSON-RPC requests (simplified MCP-style).
- `GET /health` — health and active-connection count.

Example calls:
```bash
# Open SSE stream (see heartbeats)
curl -N http://localhost:8000/sse

# Initialize
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}'

# List tools
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'

# Call the built-in echo tool
curl -X POST http://localhost:8000/message \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc":"2.0",
    "id":3,
    "method":"tools/call",
    "params":{"name":"echo","arguments":{"message":"hello SSE"}}
  }'
```

## SSE Clients

### Using MCP Python SDK

```python
from mcp import ClientSession
from mcp.client.sse import sse_client

async def main():
    async with sse_client("http://localhost:8000") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # List tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Call tool
            result = await session.call_tool("add", {"a": 5, "b": 3})
            print(f"Result: {result}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

### Using plain JavaScript

```javascript
// Open SSE connection
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Message received:', data);
};

eventSource.onerror = (error) => {
  console.error('SSE error:', error);
};

// Send JSON-RPC request
async function callTool(name, args) {
  const response = await fetch('http://localhost:8000/message', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: {
        name: name,
        arguments: args
      }
    })
  });

  return await response.json();
}

// Invoke tool
callTool('add', { a: 5, b: 3 })
  .then(result => console.log('Result:', result));
```

## Configure Claude Desktop for SSE

### Config

```json
{
  "mcpServers": {
    "calculator-sse": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

Note: Claude Desktop primarily supports STDIO today; SSE support may be limited. Check the latest docs.

## Deploying the SSE Server

### Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "sse_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build image
docker build -t mcp-sse-server .

# Run container
docker run -p 8000:8000 mcp-sse-server
```

### Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /sse {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # SSE specific settings
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 24h;
    }

    location /message {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Cloud platforms

#### Railway

```bash
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn sse_server:app --host 0.0.0.0 --port $PORT"
```

#### Fly.io

```toml
# fly.toml
app = "mcp-sse-server"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
```

## Security Considerations

### 1. Authentication

```python
from fastapi import Header, HTTPException

async def verify_token(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = authorization.replace("Bearer ", "")
    if token != "your-secret-token":
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/message", dependencies=[Depends(verify_token)])
async def handle_message(request: Request):
    # Process message
    pass
```

### 2. CORS

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Rate limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/message")
@limiter.limit("10/minute")
async def handle_message(request: Request):
    pass
```

### 4. HTTPS

Always use HTTPS in production:

```python
# Enforce HTTPS
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
app.add_middleware(HTTPSRedirectMiddleware)
```

## Monitoring and Logging

### Structured logging

```python
import logging
import structlog

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

@app.post("/message")
async def handle_message(request: Request):
    logger.info("received_request", method=request.method, path=request.url.path)
    # Handle request
```

### Health checks

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
```

### Metrics

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Visit /metrics for Prometheus metrics
```

## Best Practices

### 1. Connection management

```python
# Track active connections
active_connections: set = set()

@app.get("/sse")
async def sse_endpoint(request: Request):
    async def event_stream():
        connection_id = id(request)
        active_connections.add(connection_id)

        try:
            while True:
                if await request.is_disconnected():
                    break
                # Send data
                yield "data: ...\\n\\n"
        finally:
            active_connections.remove(connection_id)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 2. Error handling

```python
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error"
            }
        }
    )
```

### 3. Timeout configuration

```python
from fastapi import FastAPI
from uvicorn.config import Config

config = Config(
    app=app,
    timeout_keep_alive=75,  # keep-alive timeout
    timeout_graceful_shutdown=30  # graceful shutdown timeout
)
```

## Next Up

You now know MCP’s core concepts and both transports. Finally, let’s see how to integrate everything.

Continue with [07_integration.md](07_integration.md).

## References

- [MCP SSE Transport spec](https://spec.modelcontextprotocol.io/specification/basic/transports/#server-sent-events-sse)  
- [Server-Sent Events MDN](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)  
- [FastAPI SSE](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)  
- [sse-starlette](https://github.com/sysid/sse-starlette)  

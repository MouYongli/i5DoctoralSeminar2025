# STDIO Transport Method

## What is STDIO Transport?

STDIO (Standard Input/Output) is the most commonly used transport method in MCP, especially suitable for local inter-process communication.

### How It Works

```
┌──────────────┐                    ┌──────────────┐
│              │   stdin (input)    │              │
│  MCP Client  │───────────────────>│  MCP Server  │
│              │                    │              │
│              │   stdout (output)  │              │
│              │<───────────────────│              │
└──────────────┘                    └──────────────┘
```

- The client sends JSON-RPC requests through **stdin**
- The server returns JSON-RPC responses through **stdout**
- **stderr** is used for logs and error information (does not affect protocol communication)

## The Simplest MCP Server

Let's create the most basic MCP server; it doesn’t provide any functionality, only responds correctly to the client's initialization request.

### Key Concepts

1. **Initialization Handshake**: The negotiation process when a client and server establish a connection
2. **Capability Declaration**: The server informs the client of the features it supports
3. **Message Handling**: Handling JSON-RPC requests from the client

### Server Implementation Flow

```python
# 1. Import MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server

# 2. Create a server instance
app = Server("my-first-mcp-server")

# 3. Run the server
async def main():
  async with stdio_server() as (read_stream, write_stream):
    await app.run(
      read_stream,
      write_stream,
      app.create_initialization_options()
    )
```

### Key Components Explained

#### 1. Server Instance
```python
app = Server("server-name")
```
- The first parameter is the server name
- An optional second parameter specifies the version number

#### 2. stdio_server Context Manager
```python
async with stdio_server() as (read_stream, write_stream):
  # read_stream: reads client requests from stdin
  # write_stream: writes server responses to stdout
```

#### 3. Initialization Options
```python
app.create_initialization_options()
```
Returns the server's capability declaration, for example:
```json
{
  "capabilities": {
  "resources": {},
  "tools": {},
  "prompts": {}
  }
}
```

## Practical Example

For full server code examples, see:
- [scripts/01_basic_server/stdio_server.py](../scripts/01_basic_server/stdio_server.py)
- [scripts/01_basic_server/stdio_client.py](../scripts/01_basic_server/stdio_client.py)

### Testing the Server

```bash
# Using the test client
# The client will automatically start the server process and connect
uv run python scripts/01_basic_server/stdio_client.py
```

## Debugging Tips

### 1. Using logging

```python
import logging

# Configure log output to stderr (will not interfere with stdout protocol messages)
logging.basicConfig(
  level=logging.DEBUG,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)
logger.info("Server started")
```

### 2. Viewing Raw Messages

You can add a middleware layer to print all JSON-RPC messages:

```python
# Read and print requests
async for message in read_stream:
  logger.debug(f"Received request: {message}")
  # ... process message
```

### 3. Common Issues

**Q: No output after the server starts?**  
A: This is normal! The server is waiting for the client’s initialization request. Interaction happens only after the client connects.

**Q: How to know if the server is running?**  
A: Add stderr log output in the server code.

**Q: What if the server crashes?**  
A: Check stderr output; it usually contains detailed error stack information.

## Initialization Process in Detail

### 1. Client Sends Initialization Request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "roots": {
    "listChanged": true
    }
  },
  "clientInfo": {
    "name": "my-client",
    "version": "1.0.0"
  }
  }
}
```

### 2. Server Responds with Capability Declaration

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
  "protocolVersion": "2024-11-05",
  "capabilities": {
    "resources": {},
    "tools": {},
    "prompts": {}
  },
  "serverInfo": {
    "name": "my-first-mcp-server",
    "version": "1.0.0"
  }
  }
}
```

### 3. Client Sends initialized Notification

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/initialized"
}
```

At this point, the connection is established, and normal communication can begin.

## Next Steps

Now that we understand the basics of STDIO transport, let’s move on to [03_resources.md](03_resources.md) to learn how to expose resources.

## References

- [MCP STDIO Transport Specification](https://modelcontextprotocol.io/specification/2025-06-18/basic/transports)
- [Python SDK Server API](https://github.com/modelcontextprotocol/python-sdk)


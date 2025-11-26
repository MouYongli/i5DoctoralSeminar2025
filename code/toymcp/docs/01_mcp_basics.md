# MCP Basic Concepts

## What is MCP (Model Context Protocol)?

Model Context Protocol (MCP) is an open protocol developed by Anthropic that enables standardized communication between LLM applications and external data sources or tools.

### Core Value

- **Unified Interface**: Integrate once, use everywhere
- **Standardization**: Based on the JSON-RPC 2.0 protocol
- **Bidirectional Communication**: Both server and client can initiate requests
- **Extensibility**: Supports custom resources, tools, and prompts

## MCP Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│             │         │             │         │             │
│  MCP Host   │◄───────►│ MCP Client  │◄───────►│ MCP Server  │
│  (Claude)   │         │             │         │             │
│             │         │             │         │  Resources  │
└─────────────┘         └─────────────┘         │  Tools      │
                                                │  Prompts    │
                                                └─────────────┘
```

### Component Description
1. **MCP Host**
  - Examples: Claude Desktop
  - The end-user interface
  - Engages in conversation with the user
  - Connects to various servers through the MCP Client

2. **MCP Client**
  - Part of the Host (usually integrated into the Host)
  - Manages connections to multiple MCP Servers
  - Handles protocol communication

3. **MCP Server**
  - Provides specific functionalities (Resources / Tools / Prompts)
  - Multiple servers can run simultaneously
  - Each server focuses on a specific domain (e.g., file operations, databases, APIs)

## Core Features

### 1. Resources

Resources are **data** exposed by the server that the client can read.

**Characteristics:**
- Read-only data sources
- Identified by a URI
- Can be files, API data, database query results, etc.

**Examples:**
```
mcp://files/document.txt
mcp://api/users/123
mcp://database/query/latest_orders
```

### 2. Tools

Tools are **executable functions** provided by the server that the client can invoke.

**Characteristics:**
- Perform specific operations
- Have defined input parameters
- Return execution results
- May have side effects (modify data, call APIs, etc.)

**Examples:**
```python
# Calculator tool
add(a: int, b: int) -> int
multiply(a: int, b: int) -> int

# File operation tool
create_file(path: str, content: str) -> bool
```

### 3. Prompts

Prompts are predefined **conversation templates** that help users interact more effectively with LLMs.

**Characteristics:**
- Structured prompt templates
- Support parameterization
- Can include context information

**Examples:**
```
Analyze code: Please analyze the following code and provide optimization suggestions
Translate document: Translate the following content from {source_lang} to {target_lang}
```

## Transport Methods

MCP supports multiple transport protocols:

### 1. STDIO (Standard Input/Output)
- **Purpose**: Local inter-process communication
- **Advantages**: Simple, direct, low latency
- **Use cases**: Claude Desktop, local tools

### 2. SSE (Server-Sent Events)
- **Purpose**: HTTP-based communication
- **Advantages**: Supports remote connections, firewall-friendly
- **Use cases**: Web applications, remote services

## JSON-RPC 2.0

MCP communicates based on the JSON-RPC 2.0 protocol.

### Request format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}
```

### Response format
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "8"
      }
    ]
  }
}
```

## Next Steps

In [02_stdio_transport.md](02_stdio_transport.md), we will learn how to implement the simplest STDIO MCP server.

## References

- [MCP Official Documentation](https://modelcontextprotocol.io/)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)

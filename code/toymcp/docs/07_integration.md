# Integration and Practice

## Overview

How to integrate an MCP server into real applications, connect with Claude Desktop, build Python clients, and assemble a full app.

## Integrating with Claude Desktop

### Config locations

```bash
# macOS
~/Library/Application Support/Claude/claude_desktop_config.json

# Windows
%APPDATA%\\Claude\\claude_desktop_config.json

# Linux
~/.config/Claude/claude_desktop_config.json
```

### Basic config

```json
{
  "mcpServers": {
    "server-name": {
      "command": "python",
      "args": ["/path/to/your/server.py"],
      "env": {
        "API_KEY": "your-api-key"
      }
    }
  }
}
```

### Multiple servers

```json
{
  "mcpServers": {
    "file-server": {
      "command": "python",
      "args": ["/Users/you/mcp/file_server.py"]
    },
    "calculator": {
      "command": "python",
      "args": ["/Users/you/mcp/calculator.py"]
    },
    "github": {
      "command": "python",
      "args": ["/Users/you/mcp/github_server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_your_token"
      }
    }
  }
}
```

### Verify configuration

1. Restart Claude Desktop  
2. Type `/` in chat to see new tools/prompts  
3. Check Claude Desktop logs for errors  

### Debugging config issues

```bash
# macOS: tail logs
tail -f ~/Library/Logs/Claude/mcp*.log

# Manually run server
python /path/to/your/server.py

# MCP Inspector
npx @modelcontextprotocol/inspector python /path/to/your/server.py
```

## Python Client Development

### Minimal client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # Use server features
            # ...

if __name__ == "__main__":
    asyncio.run(main())
```

### Full client example

```python
import asyncio
from contextlib import asynccontextmanager
from typing import Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPClient:
    """MCP client wrapper"""

    def __init__(self, server_script: str):
        self.server_script = server_script
        self.session: Optional[ClientSession] = None

    async def connect(self):
        """Connect to MCP server"""
        server_params = StdioServerParameters(
            command="python",
            args=[self.server_script]
        )

        self.read, self.write = await stdio_client(server_params).__aenter__()
        self.session = await ClientSession(self.read, self.write).__aenter__()
        await self.session.initialize()

    async def disconnect(self):
        """Disconnect"""
        if self.session:
            await self.session.__aexit__(None, None, None)

    async def list_resources(self):
        """List resources"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.list_resources()

    async def read_resource(self, uri: str):
        """Read a resource"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.read_resource(uri)

    async def list_tools(self):
        """List tools"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.list_tools()

    async def call_tool(self, name: str, arguments: dict):
        """Call a tool"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.call_tool(name, arguments)

    async def list_prompts(self):
        """List prompts"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.list_prompts()

    async def get_prompt(self, name: str, arguments: dict = None):
        """Get a prompt"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        return await self.session.get_prompt(name, arguments or {})

@asynccontextmanager
async def mcp_client(server_script: str):
    """Context manager: auto connect/disconnect"""
    client = MCPClient(server_script)
    try:
        await client.connect()
        yield client
    finally:
        await client.disconnect()

# Usage example
async def main():
    async with mcp_client("calculator_server.py") as client:
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        result = await client.call_tool("add", {"a": 5, "b": 3})
        print(f"Result: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Integrating with an LLM

Use MCP client together with Claude (Anthropic API):

```python
import anthropic
from mcp_client import mcp_client

async def chat_with_tools():
    """Chat with Claude while using MCP tools"""

    async with mcp_client("calculator_server.py") as mcp:
        tools = await mcp.list_tools()

        claude_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
            for tool in tools
        ]

        client = anthropic.Anthropic()

        messages = []
        user_message = "Please calculate 15 + 27"

        while True:
            messages.append({
                "role": "user",
                "content": user_message
            })

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                tools=claude_tools,
                messages=messages
            )

            if response.stop_reason == "tool_use":
                tool_use = next(
                    block for block in response.content
                    if block.type == "tool_use"
                )

                tool_result = await mcp.call_tool(
                    tool_use.name,
                    tool_use.input
                )

                messages.append({
                    "role": "assistant",
                    "content": response.content
                })
                messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": tool_result.content[0].text
                        }
                    ]
                })

                continue

            print("Claude:", response.content[0].text)
            break

if __name__ == "__main__":
    asyncio.run(chat_with_tools())
```

## Full Application Example

### Project layout

```
src/toymcp/
├── __init__.py
├── server.py          # MCP server implementation
├── client.py          # Python client API
├── cli.py             # Command-line interface
└── app.py             # Application entrypoint
```

### Server implementation (server.py)

```python
"""Full MCP server implementation"""

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt, TextContent
from pathlib import Path
import asyncio

# Create server
app = Server("toymcp-server")

# === Resources ===
@app.list_resources()
async def list_resources() -> list[Resource]:
    """List resources"""
    data_dir = Path("data")
    resources = []

    if data_dir.exists():
        for file in data_dir.glob("*.txt"):
            resources.append(Resource(
                uri=f"file:///{file.name}",
                name=file.name,
                mimeType="text/plain"
            ))

    return resources

@app.read_resource()
async def read_resource(uri: str) -> str:
    """Read resource content"""
    filename = uri.replace("file:///", "")
    file_path = Path("data") / filename

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filename}")

    return file_path.read_text()

# === Tools ===
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List tools"""
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
        ),
        Tool(
            name="create_file",
            description="Create a text file",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a tool"""
    if name == "add":
        result = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(result))]

    elif name == "create_file":
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)

        file_path = data_dir / arguments["filename"]
        file_path.write_text(arguments["content"])

        return [TextContent(
            type="text",
            text=f"File created: {file_path}"
        )]

    raise ValueError(f"Unknown tool: {name}")

# === Prompts ===
@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List prompts"""
    return [
        Prompt(
            name="analyze",
            description="Analysis helper",
            arguments=[]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict):
    """Return prompt"""
    if name == "analyze":
        return {
            "description": "Data analysis helper",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": "Please help analyze the following data..."
                    }
                }
            ]
        }

    raise ValueError(f"Unknown prompt: {name}")

# === Run server ===
async def main():
    """Run server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

### Client API (client.py)

Reuse the `MCPClient` class defined earlier.

### CLI (cli.py)

```python
"""Command-line interface"""

import click
import asyncio
from pathlib import Path
from .client import mcp_client

@click.group()
def cli():
    """ToyMCP CLI"""
    pass

@cli.command()
def start_server():
    """Start MCP server"""
    from .server import main
    asyncio.run(main())

@cli.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def add(a: float, b: float):
    """Add two numbers"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(str(server_script)) as client:
            result = await client.call_tool("add", {"a": a, "b": b})
            click.echo(f"Result: {result.content[0].text}")

    asyncio.run(run())

@cli.command()
def list_resources():
    """List resources"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(str(server_script)) as client:
            resources = await client.list_resources()
            for res in resources:
                click.echo(f"- {res.name} ({res.uri})")

    asyncio.run(run())

@cli.command()
@click.argument("uri")
def read(uri: str):
    """Read a resource"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(str(server_script)) as client:
            content = await client.read_resource(uri)
            click.echo(content)

    asyncio.run(run())

if __name__ == "__main__":
    cli()
```

### Entrypoint (app.py)

```python
"""Application entrypoint"""

def main():
    """Entrypoint"""
    from .cli import cli
    cli()

if __name__ == "__main__":
    main()
```

### pyproject.toml

```toml
[project]
name = "toymcp"
version = "0.1.0"
dependencies = [
    "mcp>=0.1.0",
    "click>=8.0.0",
    "anthropic>=0.18.0"
]

[project.scripts]
toymcp = "toymcp.app:main"

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-asyncio"
]
```

### Usage

```bash
# Install
pip install -e .

# Start server
toymcp start-server

# CLI commands
toymcp add 5 3
toymcp list-resources
toymcp read file:///example.txt

# Python API
python -c "
from toymcp.client import mcp_client
import asyncio

async def main():
    async with mcp_client('server.py') as client:
        result = await client.call_tool('add', {'a': 5, 'b': 3})
        print(result.content[0].text)

asyncio.run(main())
"
```

## Best Practices Checklist

### 1. Server design

- ✅ Single responsibility: each server focuses on one domain  
- ✅ Clear names: meaningful tool/resource/prompt names  
- ✅ Good docs: detailed descriptions  
- ✅ Error handling: helpful error messages  
- ✅ Logging: write to stderr  

### 2. Client development

- ✅ Context management: use `async with` for cleanup  
- ✅ Retry on transient errors  
- ✅ Timeouts: set reasonable limits  
- ✅ Type hints: add Python typing  

### 3. Production

- ✅ Env vars for secrets  
- ✅ Monitoring/alerting for key metrics  
- ✅ Graceful shutdown on SIGTERM  
- ✅ Health checks (SSE or HTTP)  
- ✅ Semantic versioning  

### 4. Security

- ✅ Input validation  
- ✅ Path safety: prevent traversal  
- ✅ Least privilege  
- ✅ Avoid logging secrets  

## Testing

### Unit tests

```python
import pytest
from toymcp.server import app

@pytest.mark.asyncio
async def test_add_tool():
    """Test add tool"""
    result = await app.call_tool("add", {"a": 5, "b": 3})
    assert result[0].text == "8"

@pytest.mark.asyncio
async def test_list_tools():
    """Test tool listing"""
    tools = await app.list_tools()
    tool_names = [t.name for t in tools]
    assert "add" in tool_names
```

### Integration test

```python
@pytest.mark.asyncio
async def test_full_workflow():
    """Test full workflow"""
    async with mcp_client("server.py") as client:
        result = await client.call_tool("add", {"a": 5, "b": 3})
        assert result.content[0].text == "8"

        resources = await client.list_resources()
        assert len(resources) > 0
```

## Summary

You now have:

1. ✅ MCP fundamentals and architecture  
2. ✅ STDIO and SSE transports  
3. ✅ Resources, tools, and prompts implementations  
4. ✅ Claude Desktop integration  
5. ✅ Python client development  
6. ✅ Full application assembly  

## Next Steps

- 🚀 Build your own MCP server  
- 🌟 Explore [official MCP server examples](https://github.com/modelcontextprotocol/servers)  
- 📖 Read the [full MCP spec](https://spec.modelcontextprotocol.io/)  
- 🤝 Join the [MCP community](https://github.com/modelcontextprotocol)  

## References

- [Official MCP docs](https://modelcontextprotocol.io/)  
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)  
- [Server examples](https://github.com/modelcontextprotocol/servers)  
- [Claude Desktop](https://claude.ai/download)  

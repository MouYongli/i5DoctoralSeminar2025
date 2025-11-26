# Tools

## What Are Tools?

Tools are **executable functions** provided by an MCP server that let an LLM (such as Claude) perform concrete actions.

### Tools vs Resources

| Feature | Resources | Tools |
|------|-----------------|--------------|
| Purpose | Read-only data | Executable actions |
| Side effects | None | Possible |
| Examples | Read files, query data | Create files, call APIs, compute |

### Usage Scenarios

- 🔧 System operations (create files, run commands)
- 🧮 Computation (math, data processing)
- 🌐 API calls (send requests, update data)
- 📝 Data mutation (database writes, file edits)
- 🔍 Complex queries (search, filter, aggregate)

## Anatomy of a Tool

### 1. Tool Definition

```python
{
  "name": "add",
  "description": "Add two numbers",
  "inputSchema": {
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
}
```

### 2. Tool Invocation

Client request:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
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

### 3. Tool Response

Server returns:

```json
{
  "jsonrpc": "2.0",
  "id": 2,
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

## Building a Tool Server

### Core Methods

#### 1. List tools (`tools/list`)

```python
from mcp.types import Tool

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Add two numbers",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers",
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
```

#### 2. Call tools (`tools/call`)

```python
from mcp.types import TextContent, CallToolResult

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add":
        a = arguments["a"]
        b = arguments["b"]
        result = a + b
        return [TextContent(type="text", text=str(result))]

    elif name == "multiply":
        a = arguments["a"]
        b = arguments["b"]
        result = a * b
        return [TextContent(type="text", text=str(result))]

    else:
        raise ValueError(f"Unknown tool: {name}")
```

## Example: Calculator Tool

Implement a fully featured calculator tool server.

### Features

- ✅ Addition (`add`)
- ✅ Subtraction (`subtract`)
- ✅ Multiplication (`multiply`)
- ✅ Division (`divide`)
- ✅ Power (`power`)
- ✅ Square root (`sqrt`)

### Full Implementation

```python
import math
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("calculator-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Addition: a + b",
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
            name="divide",
            description="Division: a / b",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Dividend"},
                    "b": {"type": "number", "description": "Divisor (must not be 0)"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="sqrt",
            description="Square root: √x",
            inputSchema={
                "type": "object",
                "properties": {
                    "x": {"type": "number", "description": "Radicand (must be ≥ 0)"}
                },
                "required": ["x"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "add":
            result = arguments["a"] + arguments["b"]
        elif name == "subtract":
            result = arguments["a"] - arguments["b"]
        elif name == "multiply":
            result = arguments["a"] * arguments["b"]
        elif name == "divide":
            if arguments["b"] == 0:
                return [TextContent(
                    type="text",
                    text="Error: divisor cannot be 0"
                )]
            result = arguments["a"] / arguments["b"]
        elif name == "power":
            result = arguments["a"] ** arguments["b"]
        elif name == "sqrt":
            if arguments["x"] < 0:
                return [TextContent(
                    type="text",
                    text="Error: cannot take square root of a negative number"
                )]
            result = math.sqrt(arguments["x"])
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=str(result))]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Execution error: {str(e)}"
        )]
```

### Full Example Code

See [scripts/03_tools/calculator_tool_server.py](../scripts/03_tools/calculator_tool_server.py).

## InputSchema Overview

InputSchema uses [JSON Schema](https://json-schema.org/) to define parameters.

### Basic Types

```python
# Numbers
{"type": "number"}
{"type": "integer"}

# Strings
{"type": "string"}
{"type": "string", "minLength": 1, "maxLength": 100}

# Boolean
{"type": "boolean"}

# Array
{"type": "array", "items": {"type": "string"}}

# Object
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "number"}
  }
}
```

### Advanced Features

```python
# Enum
{
  "type": "string",
  "enum": ["red", "green", "blue"],
  "description": "Pick a color"
}

# Numeric range
{
  "type": "number",
  "minimum": 0,
  "maximum": 100
}

# Pattern
{
  "type": "string",
  "pattern": "^[a-zA-Z0-9]+$"
}

# Default value
{
  "type": "string",
  "default": "default_value"
}
```

### Complex Example

```python
{
  "type": "object",
  "properties": {
    "operation": {
      "type": "string",
      "enum": ["create", "update", "delete"],
      "description": "Operation to perform"
    },
    "target": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"}
      },
      "required": ["id"]
    },
    "options": {
      "type": "object",
      "properties": {
        "force": {"type": "boolean", "default": false},
        "timeout": {"type": "number", "minimum": 0}
      }
    }
  },
  "required": ["operation", "target"]
}
```

## Tool Response Types

Tools can return multiple content types:

### 1. Text content

```python
TextContent(type="text", text="Success")
```

### 2. Image content

```python
ImageContent(
    type="image",
    data="base64_encoded_image_data",
    mimeType="image/png"
)
```

### 3. Embedded resources

```python
EmbeddedResource(
    type="resource",
    resource=Resource(
        uri="file:///result.txt",
        name="Result file",
        mimeType="text/plain",
        text="Tool output..."
    )
)
```

### 4. Mixed content

```python
[
    TextContent(type="text", text="Operation completed. Results:"),
    ImageContent(type="image", data="...", mimeType="image/png"),
    TextContent(type="text", text="Details saved to file.")
]
```

## Best Practices

### 1. Clear tool descriptions

```python
# ❌ Vague
Tool(name="process", description="Handle data")

# ✅ Clear
Tool(
    name="process_user_data",
    description="Validate and process user data including format checks, deduplication, and normalization"
)
```

### 2. Detailed parameter notes

```python
inputSchema={
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "description": "User email address; must be valid email format",
            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        }
    }
}
```

### 3. Robust error handling

```python
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        # Validate arguments
        if not isinstance(arguments.get("value"), int):
            return [TextContent(
                type="text",
                text="Error: parameter 'value' must be an integer"
            )]

        # Perform operation
        result = perform_operation(arguments)

        return [TextContent(type="text", text=f"Success: {result}")]

    except ValueError as e:
        return [TextContent(type="text", text=f"Parameter error: {str(e)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Execution failed: {str(e)}")]
```

### 4. Async operations

```python
import asyncio

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "fetch_data":
        # Async HTTP request
        async with aiohttp.ClientSession() as session:
            async with session.get(arguments["url"]) as response:
                data = await response.text()
                return [TextContent(type="text", text=data)]
```

### 5. Progress feedback (via logs)

```python
import logging
logger = logging.getLogger(__name__)

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Starting tool: {name}")

    # Long-running operation
    for i in range(10):
        logger.info(f"Progress: {i+1}/10")
        await asyncio.sleep(0.5)

    logger.info("Completed")
    return [TextContent(type="text", text="Done")]
```

## Testing Tools

### Using Claude Desktop

1. Configure `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "calculator": {
      "command": "python",
      "args": ["scripts/03_tools/calculator_tool_server.py"]
    }
  }
}
```

2. Restart Claude Desktop

3. Try in chat:
```
Please calculate 15 + 27
Please compute the square root of 144
```

### Using Python Client

```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # List tools
        tools = await session.list_tools()

        # Call tool
        result = await session.call_tool("add", {"a": 5, "b": 3})
        print(result.content[0].text)  # "8"
```

## Next Up

Tools enable Claude to act, but sometimes we need to guide the conversation with **prompt templates**.

Continue with [05_prompts.md](05_prompts.md).

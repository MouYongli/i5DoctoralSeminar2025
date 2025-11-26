# Resources

## What Are Resources?

Resources are **read-only data** exposed by an MCP server, which clients (such as Claude) can read and use as context.

### Characteristics of Resources

- **Read-only**: Resources are data sources and cannot be modified via MCP
- **URI identifier**: Each resource has a unique URI
- **Typed**: Supports text, images, binary data, and more
- **Dynamic**: Resource content can be generated dynamically

### Common Use Cases

- File system access
- API data
- Database query results
- Log files
- Configuration information

## Components of a Resource

### 1. Resource URI

URIs uniquely identify resources, with a flexible format:

```python
# File resource
"file:///path/to/document.txt"

# Custom protocol
"myapp://users/123"
"db://query/latest_orders"

# RESTful style
"resource://api/v1/data"
```

### 2. Resource Metadata

```python
{
    "uri": "file:///example.txt",
    "name": "Example Document",
    "description": "This is an example document",
    "mimeType": "text/plain"
}
```

### 3. Resource Content

```python
{
    "uri": "file:///example.txt",
    "mimeType": "text/plain",
    "text": "Actual content of the file..."
}
```

## Implementing a Resource Server

### Core Methods

#### 1. List Resources (`resources/list`)

The client calls this method to get a list of all available resources.

```python
@app.list_resources()
async def list_resources() -> list[Resource]:
        return [
                Resource(
                        uri="file:///document1.txt",
                        name="Document 1",
                        description="First example document",
                        mimeType="text/plain"
                ),
                Resource(
                        uri="file:///document2.txt",
                        name="Document 2",
                        description="Second example document",
                        mimeType="text/plain"
                )
        ]
```

#### 2. Read Resource (`resources/read`)

The client calls this method to get the content of a specific resource.

```python
@app.read_resource()
async def read_resource(uri: str) -> str:
        if uri == "file:///document1.txt":
                return "This is the content of Document 1"
        elif uri == "file:///document2.txt":
                return "This is the content of Document 2"
        else:
                raise ValueError(f"Unknown resource: {uri}")
```

## Practical Example: File System Resources

Let's implement a simple file resource server that exposes files from a specific directory.

### Feature Design

- List all files in the directory
- Read file contents
- Support text files
- Security checks (prevent directory traversal attacks)

### Implementation Steps

```python
from pathlib import Path
from mcp.server import Server
from mcp.types import Resource, TextContent

# 1. Define working directory
RESOURCE_DIR = Path(__file__).parent / "data"

# 2. List resources
@app.list_resources()
async def list_resources() -> list[Resource]:
        resources = []
        for file_path in RESOURCE_DIR.glob("*.txt"):
                resources.append(Resource(
                        uri=f"file:///{file_path.name}",
                        name=file_path.name,
                        description=f"Text file: {file_path.name}",
                        mimeType="text/plain"
                ))
        return resources

# 3. Read resource
@app.read_resource()
async def read_resource(uri: str) -> str:
        # Security check: only allow reading files in the working directory
        filename = uri.replace("file:///", "")
        file_path = RESOURCE_DIR / filename

        if not file_path.is_relative_to(RESOURCE_DIR):
                raise ValueError("Access to files outside the directory is denied")

        if not file_path.exists():
                raise FileNotFoundError(f"File does not exist: {filename}")

        return file_path.read_text(encoding="utf-8")
```

### Full Example

See [scripts/02_resources/file_resource_server.py](../scripts/02_resources/file_resource_server.py)

## Resource Templates

For dynamic resources, you can use resource templates:

```python
{
    "uriTemplate": "users/{user_id}/posts/{post_id}",
    "name": "User Post",
    "description": "Get a specific post from a specific user"
}
```

A client can generate a concrete URI from parameters:
```
users/123/posts/456
```

### Implementing Template Resources

```python
from mcp.types import ResourceTemplate

@app.list_resource_templates()
async def list_templates() -> list[ResourceTemplate]:
        return [
                ResourceTemplate(
                        uriTemplate="users/{user_id}",
                        name="User Info",
                        description="Get detailed information about a user"
                )
        ]

@app.read_resource()
async def read_resource(uri: str) -> str:
        # Parse URI: "users/123"
        if uri.startswith("users/"):
                user_id = uri.split("/")[1]
                # Fetch user info from database or API
                return f"Information about user {user_id}..."
```

## Best Practices

### 1. Security

```python
# ❌ Insecure: allows arbitrary file access
file_path = Path(uri)

# ✅ Secure: restrict to a specific directory
base_dir = Path("/safe/directory")
file_path = base_dir / filename
if not file_path.is_relative_to(base_dir):
        raise ValueError("Invalid path")
```

### 2. Error Handling

```python
@app.read_resource()
async def read_resource(uri: str) -> str:
        try:
                # Read resource
                return content
        except FileNotFoundError:
                raise ValueError(f"Resource not found: {uri}")
        except PermissionError:
                raise ValueError(f"No permission to access: {uri}")
        except Exception as e:
                raise ValueError(f"Failed to read: {str(e)}")
```

### 3. Performance Optimization

```python
# For large files, consider chunked reading or caching
from functools import lru_cache

@lru_cache(maxsize=100)
def get_file_content(file_path: str) -> str:
        return Path(file_path).read_text()
```

### 4. Rich Metadata

```python
Resource(
        uri="file:///data.json",
        name="User Data",
        description="Contains detailed information about all users (JSON format)",
        mimeType="application/json",
        # Supports custom metadata
)
```

## Practical Example

### Testing the Resource Server

### Using MCP Inspector

```bash
# Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# Inspect the server
mcp-inspector python scripts/02_resources/file_resource_server.py
```

### Using Python Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async with stdio_client(
        StdioServerParameters(
                command="python",
                args=["scripts/02_resources/file_resource_server.py"]
        )
) as (read, write):
        async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()

                # List resources
                resources = await session.list_resources()
                print(f"Available resources: {resources}")

                # Read resource
                content = await session.read_resource("file:///example.txt")
                print(f"Content: {content}")
```

For full server code examples, see:
- [scripts/02_resources/file_resource_server.py](../scripts/02_resources/file_resource_server.py)

```bash
# Using the test client
# The client will automatically start the server process and connect
uv run python scripts/02_resources/file_resource_client.py 
```

## Next Step

Resources let Claude access data, but to perform operations, we need **tools**.

Continue to [04_tools.md](04_tools.md) to learn how to implement executable tools.

## References

- [MCP Resources Specification](https://modelcontextprotocol.io/specification/2025-06-18/server/resources/)
- [Resource Type Definitions](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/types.py)

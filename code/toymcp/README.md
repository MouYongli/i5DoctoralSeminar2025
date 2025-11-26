# ToyMCP - Model Context Protocol Learning Project

A comprehensive Python learning project for the Model Context Protocol (MCP), featuring detailed documentation, example code, and practical implementation.

## Quick Start

### Environment Setup and Dependency Installation

```bash
# Create virtual environment with Python 3.12
uv venv --python 3.12

# Activate the virtual environment
# source .venv/bin/activate

# Install dependencies
uv sync

# Editable install (development mode)
uv pip install -e .
```

### Running the Server

```bash
# Start the MCP server
toymcp start-server

# Or run directly
python src/toymcp/server.py
```

### Using the CLI

```bash
# Show help
toymcp --help

# File operations
toymcp file create test.txt --content "Hello MCP"
toymcp file read test.txt
toymcp file list

# Calculator
toymcp calc add 5 3
toymcp calc sqrt 16

# Show server information
toymcp info
```

### Using as a Python Library

```python
from toymcp.client import mcp_client
import asyncio

async def main():
    async with mcp_client("src/toymcp/server.py") as client:
        # Call tools
        result = await client.calculate("add", 5, 3)
        print(result)  # "Result: 8"

        # Create file
        await client.create_file("test.txt", "Hello MCP!")

asyncio.run(main())
```

```
┌─────────────────┐
│   User (CLI)    │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────┐
│  Chat Agent (chat_agent.py)     │
│  - Dialogue management          │
│  - Tool invocation orchestration│
└───┬─────────────────────┬───────┘
    │                     │
    ↓                     ↓
┌──────────────┐   ┌──────────────┐
│ LLM Client   │   │  MCP Client  │
│ (Azure GPT)  │   │              │
└──────────────┘   └──────┬───────┘
                          │
                          ↓
                   ┌──────────────┐
                   │  MCP Server  │
                   │ - Resources  │
                   │ - Tools      │
                   │ - Prompts    │
                   └──────────────┘
```

## Project Structure

```
toymcp/
├── docs/                           # 📖 Learning Documentation (Progressive)
│   ├── 01_mcp_basics.md           # MCP Fundamentals
│   ├── 02_stdio_transport.md      # STDIO Transport
│   ├── 03_resources.md            # Resources
│   ├── 04_tools.md                # Tools
│   ├── 05_prompts.md              # Prompts
│   ├── 06_sse_transport.md        # SSE Transport
│   └── 07_integration.md          # Integration & Practice
│
├── scripts/                        # 🔧 Step-by-Step Examples
│   ├── 01_basic_server/           # Basic MCP Server
│   │   ├── stdio_server.py
│   │   └── stdio_client.py
│   ├── 02_resources/              # Resource Examples
│   │   └── file_resource_server.py
│   ├── 03_tools/                  # Tool Examples
│   │   └── calculator_tool_server.py
│   ├── 04_prompts/                # Prompt Examples
│   │   └── prompt_template_server.py
│   ├── 05_sse_server/             # SSE Transport Examples
│   │   └── sse_server.py
│   └── 06_combined/               # Full-Featured Examples
│       └── full_featured_server.py
│
├── src/toymcp/
│   ├── llm_client.py       # Added: Azure OpenAI wrapper
│   ├── chat_agent.py       # Added: conversation engine
│   ├── cli.py              # Updated: added chat command
│   ├── server.py           # Existing: MCP server
│   └── client.py           # Existing: MCP client
│
├── .env.example            # Added: configuration template
│
├── notebooks/                      # 📓 Jupyter Notebooks
│   └── hello_world.ipynb
│
├── pyproject.toml                  # Project Configuration
└── README.md                       # This File
```

## Learning Paths

### Approach 1: Progressive Learning (Recommended)

Follow the documentation in the `docs/` directory:
0. **[00_overview.md](docs/00_overview.md)** - Overview of MCP
1. **[01_mcp_basics.md](docs/01_mcp_basics.md)** - Understanding MCP Core Concepts
2. **[02_stdio_transport.md](docs/02_stdio_transport.md)** - Learning STDIO Transport
3. **[03_resources.md](docs/03_resources.md)** - Implementing Resources
4. **[04_tools.md](docs/04_tools.md)** - Implementing Tools
5. **[05_prompts.md](docs/05_prompts.md)** - Implementing Prompts
6. **[06_sse_transport.md](docs/06_sse_transport.md)** - Learning SSE Transport
7. **[07_integration.md](docs/07_integration.md)** - Integration with Applications

Each document comes with corresponding runnable example code in the `scripts/` directory.

### Approach 2: Example-Driven Learning

Run the examples in the `scripts/` directory from basic to advanced:

```bash
# 1. Basic server
python scripts/01_basic_server/stdio_server.py

# 2. Test client connection
python scripts/01_basic_server/stdio_client.py

# 3. Resources functionality
python scripts/02_resources/file_resource_server.py

# 4. Tools functionality
python scripts/03_tools/calculator_tool_server.py

# 5. Prompts functionality
python scripts/04_prompts/prompt_template_server.py

# 6. SSE server (requires sse dependency group)
# uv sync --group sse
python scripts/05_sse_server/sse_server.py

# 7. Full-featured server
python scripts/06_combined/full_featured_server.py
```

### Approach 3: Using the Complete Implementation

Use the complete implementation in `src/toymcp/`:

```bash
# As a CLI tool
toymcp start-server
toymcp file create test.txt
toymcp calc add 5 3

# As a Python library
from toymcp.client import mcp_client
```

## 💡 Core Features

### Resources

Expose data for AI to read:

```python
# List resources
toymcp list-resources

# Read resource
toymcp read-resource file:///welcome.txt
```

### Tools

Provide executable functions:

- ✅ File Operations: `create_file`, `read_file`, `delete_file`, `list_files`
- ✅ Calculator: `calculate` (supports add, subtract, multiply, divide, power, sqrt)

```python
# Use tools
toymcp file create hello.txt --content "Hello"
toymcp calc add 10 20
```

### Prompts

Pre-defined conversation templates:

- ✅ Code Review: `code_review`
- ✅ Debug Helper: `debug_help`

```python
# Get prompt
toymcp get-prompt code_review --language Python
```

## 🔌 Integration with Claude Desktop

### Configuration File

Edit the Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Configuration Example

```json
{
  "mcpServers": {
    "toymcp": {
      "command": "python",
      "args": ["/absolute/path/to/toymcp/src/toymcp/server.py"]
    }
  }
}
```

After restarting Claude Desktop, you can use ToyMCP's tools and resources in conversations.

## 🧪 Running Tests

```bash
# Install test dependencies (using PEP 735 dependency groups)
uv sync --group dev

# Run tests (to be implemented)
pytest
```

## MCP Learning Resources

### Official Resources

- [MCP Official Documentation](https://modelcontextprotocol.io)
- [MCP Specification](https://spec.modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Official Server Examples](https://github.com/modelcontextprotocol/servers)

### Courses & Tutorials

- [Microsoft MCP for Beginners](https://github.com/microsoft/mcp-for-beginners) - Complete 9-module course
- [Hugging Face MCP Course](https://huggingface.co/learn/mcp-course) - In collaboration with Anthropic
- [Anthropic Official Course](https://anthropic.skilljar.com/introduction-to-model-context-protocol)
- [DataCamp MCP Tutorial](https://www.datacamp.com/tutorial/mcp-model-context-protocol)

### Community

- [MCP GitHub Discussions](https://github.com/modelcontextprotocol/python-sdk/discussions)
- [Anthropic Discord](https://discord.gg/anthropic)

## 🛠️ Development Guide

### Adding Dependencies

```bash
# Regular dependencies
uv add <package-name>

# Development dependencies (PEP 735)
uv add --group dev <package-name>

# SSE-related dependencies
uv add --group sse <package-name>

# Install all dependency groups
uv sync --all-groups
```

### Project Commands

```bash
# Sync dependencies
uv sync

# Run server
toymcp start-server

# View all commands
toymcp --help
```

### Jupyter Notebook

```bash
# Open .ipynb file in VS Code
# Select the project's .venv as kernel

# Or manually register kernel
uv run python -m ipykernel install --user --name=toymcp
```

## 🎯 Learning Recommendations

1. **📖 Read Documentation First** - Start with `docs/01_mcp_basics.md`
2. **🔧 Run Examples** - Execute code in `scripts/`
3. **💻 Hands-On Practice** - Modify examples and implement your own features
4. **🚀 Build Projects** - Use `src/toymcp` as a starting point
5. **🤝 Integrate Applications** - Connect to Claude Desktop or your own AI applications

## TODO

- [ ] Add more tool examples
- [ ] Improve test coverage
- [ ] Add more prompt templates
- [ ] Complete SSE server implementation
- [ ] Performance optimization and monitoring
- [ ] Docker deployment examples

---

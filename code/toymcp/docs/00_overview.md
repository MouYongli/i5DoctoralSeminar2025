# ToyMCP Project Overview

## Welcome

Welcome to ToyMCP - a project specifically designed for learning the Model Context Protocol (MCP). This project provides a complete learning path from basics to practice.

## Documentation Structure

The project documentation is organized by difficulty level and should be read in sequence:

### Basics

1. **[01_mcp_basics.md](01_mcp_basics.md)**
   - What is MCP?
   - Core concepts: Resources, Tools, Prompts
   - Architecture and transport methods
   - JSON-RPC 2.0 fundamentals

### Transport Methods

2. **[02_stdio_transport.md](02_stdio_transport.md)**
   - STDIO transport principles
   - The simplest MCP stdio server
   - Detailed initialization process
   - Debugging tips

### Three Core Features

3. **[03_resources.md](03_resources.md)**
   - Resource concepts and applications
   - URI design
   - File system resource implementation
   - Resource templates (dynamic resources)
   - Security and performance considerations

4. **[04_tools.md](04_tools.md)**
   - Tool concepts and applications
   - InputSchema design
   - Calculator example
   - Error handling
   - Best practices

5. **[05_prompts.md](05_prompts.md)**
   - The role of prompts
   - Parameterized prompts
   - Development assistant templates
   - Advanced techniques

### Advanced Topics

6. **[06_sse_transport.md](06_sse_transport.md)**
   - SSE transport method
   - HTTP-based MCP services
   - Implementation with FastAPI
   - Deployment and security

7. **[07_integration.md](07_integration.md)**
   - Integration with Claude Desktop
   - Python client development
   - Complete application examples
   - Testing and deployment

## 🔧 Code Example Structure

Each document corresponds to runnable code in the `scripts/` directory:

```
scripts/
├── 01_basic_server/        ← Corresponds to 02_stdio_transport.md
├── 02_resources/           ← Corresponds to 03_resources.md
├── 03_tools/               ← Corresponds to 04_tools.md
├── 04_prompts/             ← Corresponds to 05_prompts.md
├── 05_sse_server/          ← Corresponds to 06_sse_transport.md
└── 06_combined/            ← Corresponds to 07_integration.md
```

## 🎯 Learning Recommendations

### Beginner's Path

If you're new to MCP, we recommend:

1. **Day 1**: Read `01_mcp_basics.md`, understand core concepts
2. **Day 2**: Read `02_stdio_transport.md`, run `scripts/01_basic_server/`
3. **Days 3-5**: Learn Resources, Tools, Prompts in sequence (docs 03-05)
4. **Day 6**: Read `06_sse_transport.md` (optional)
5. **Day 7**: Read `07_integration.md`, build a complete application

### Practitioner's Path

If you want to get started quickly:

1. Directly examine the complete implementation in `src/toymcp/`
2. Run the `toymcp` CLI tool to experience the features
3. Read `07_integration.md` to understand integration methods
4. Go back to learn specific concepts as needed

### Developer's Path

If you want to develop an MCP server:

1. Quickly browse `01_mcp_basics.md` to understand concepts
2. Deep dive into the feature documentation you need (03-05)
3. Reference the complete example in `scripts/06_combined/`
4. Use `src/toymcp/` as a project template

## 🚀 Quick Start

### Run Your First Example

```bash
# 1. Run the most basic server
python scripts/01_basic_server/stdio_server.py

# 2. Test in another terminal
python scripts/01_basic_server/stdio_client.py
```

### Use Full Features

```bash
# Install the project
uv pip install -e .

# Start the server
toymcp start-server

# Use the CLI
toymcp file create test.txt --content "Hello MCP"
toymcp calc add 5 3
```

## Core Concepts Quick Reference

### Resources

- **Purpose**: Expose read-only data
- **Examples**: Files, database queries, API data
- **Methods**: `list_resources()`, `read_resource(uri)`

### Tools

- **Purpose**: Provide executable functions
- **Examples**: Calculations, file operations, API calls
- **Methods**: `list_tools()`, `call_tool(name, args)`

### Prompts

- **Purpose**: Pre-defined conversation templates
- **Examples**: Code review, debugging assistant
- **Methods**: `list_prompts()`, `get_prompt(name, args)`

### Code Files

- `scripts/*` - **Simplest** example
- `src/toymcp/server.py` - **Production-grade** implementation
- `src/toymcp/client.py` - Client API
- `src/toymcp/cli.py` - Command-line tool

## FAQ

### Q: Where should I start?

**A**: Start with [01_mcp_basics.md](01_mcp_basics.md), then run `scripts/01_basic_server/stdio_client.py` to test the connection.

### Q: How do I quickly set up my own server?

**A**: Copy `src/toymcp/server.py` as a starting point and modify the tool and resource definitions within it.

### Q: What's the difference between STDIO and SSE?

**A**:
- STDIO: Local process communication, suitable for Claude Desktop
- SSE: HTTP communication, suitable for remote deployment

### Q: How do I debug an MCP server?

**A**:
1. Use `logging` to output to `stderr`
2. Use the `mcp-inspector` tool
3. Check Claude Desktop logs

### Q: Which should I use - Resources, Tools, or Prompts?

**A**:
- Read-only data → Use Resources
- Need to execute operations → Use Tools
- Guide conversations → Use Prompts

## Learning Checklist

After completing each stage, check if you've mastered:

### Basics Stage

- [ ] Understand the purpose and value of MCP
- [ ] Know the differences between Resources, Tools, and Prompts
- [ ] Understand JSON-RPC 2.0 communication mechanism

### Practice Stage

- [ ] Successfully run the basic server
- [ ] Implement at least one Resource
- [ ] Implement at least one Tool
- [ ] Create at least one Prompt

### Integration Stage

- [ ] Configure Claude Desktop connection
- [ ] Write a Python client
- [ ] Understand how to deploy a server

## MCP Learning Resources
After completing this project, you can continue exploring:

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

- [MCP GitHub Issues](https://github.com/modelcontextprotocol/python-sdk/issues)
**Advanced Topics**: Performance optimization, security hardening, distributed deployment
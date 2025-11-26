"""
ToyMCP CLI - Command Line Interface

Provides command-line tools for operating MCP servers
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

import click

from toymcp.client import mcp_client
from toymcp.server import create_server


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """
    ToyMCP - Model Context Protocol Learning Project

    Command-line tool providing MCP server and client functionality
    """
    pass


# ========================================
# Server commands
# ========================================

@cli.command()
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Working directory path"
)
def start_server(work_dir: Optional[Path]):
    """Start MCP server"""
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    async def run():
        server = create_server(work_dir=work_dir)
        await server.run()

    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        click.echo("Server stopped", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


# ========================================
# Intelligent conversation commands
# ========================================

@cli.command()
@click.option(
    "--work-dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Working directory path (note storage location)"
)
@click.option(
    "--api-key",
    default=None,
    help="Azure OpenAI API key (can be read from environment variable)"
)
@click.option(
    "--api-base",
    default=None,
    help="Azure OpenAI API endpoint (can be read from environment variable)"
)
def chat(work_dir: Optional[Path], api_key: Optional[str], api_base: Optional[str]):
    """Start intelligent study notes assistant (AI chat mode)"""
    import logging
    from toymcp.chat_agent import ChatAgent
    from toymcp.llm_client import LLMClient

    # Configure logging (output to stderr only to avoid interfering with conversation)
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    async def run_chat():
        # Get server script path
        server_script = Path(__file__).parent / "server.py"

        # Create LLM client
        try:
            llm_client = LLMClient(
                api_key=api_key,
                api_base=api_base,
            )
        except ValueError as e:
            click.echo(f"❌ Configuration error: {e}", err=True)
            click.echo("Please set environment variables or use --api-key and --api-base options", err=True)
            click.echo("Tip: Copy .env.example to .env and fill in configuration", err=True)
            sys.exit(1)

        # Connect to MCP server
        async with mcp_client(server_script) as mcp_client_inst:
            # Set working directory environment variable (for server use)
            if work_dir:
                os.environ['TOYMCP_WORK_DIR'] = str(work_dir)

            # Create chat agent
            agent = ChatAgent(mcp_client_inst, llm_client)

            # Initialize agent (load tools)
            try:
                await agent.initialize()
            except Exception as e:
                click.echo(f"❌ Initialization failed: {e}", err=True)
                sys.exit(1)

            # Display welcome message
            click.echo("=" * 60)
            click.echo("🤖 Intelligent Study Notes Assistant")
            click.echo("=" * 60)
            click.echo("I can help you:")
            click.echo("  • Create and manage study notes")
            click.echo("  • Calculate study progress")
            click.echo("  • Provide code review and debugging suggestions")
            click.echo()
            click.echo("Type 'quit' or 'exit' to exit")
            click.echo("Type 'clear' to clear conversation history")
            click.echo("Type 'help' to show help")
            click.echo("=" * 60)
            click.echo()

            # Conversation loop
            while True:
                try:
                    # Get user input
                    user_input = input("You: ").strip()

                    if not user_input:
                        continue

                    # Handle special commands
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        click.echo("\n👋 Goodbye!")
                        break

                    if user_input.lower() == 'clear':
                        agent.clear_conversation()
                        click.echo("✓ Conversation history cleared\n")
                        continue

                    if user_input.lower() == 'help':
                        click.echo("\nAvailable commands:")
                        click.echo("  quit/exit  - Exit program")
                        click.echo("  clear      - Clear conversation history")
                        click.echo("  help       - Show this help")
                        click.echo()
                        continue

                    # Send to AI for processing
                    try:
                        response = await agent.chat(user_input)
                        click.echo(f"\n🤖 Assistant: {response}\n")
                    except Exception as e:
                        click.echo(f"\n❌ Error: {e}\n", err=True)

                except KeyboardInterrupt:
                    click.echo("\n\n👋 Goodbye!")
                    break
                except EOFError:
                    click.echo("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    click.echo(f"\n❌ Error occurred: {e}\n", err=True)

    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        click.echo("\nProgram exited", err=True)
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        sys.exit(1)


# ========================================
# File operation commands
# ========================================

@cli.group()
def file():
    """File operation commands"""
    pass


@file.command("create")
@click.argument("filename")
@click.option("--content", "-c", default="", help="File content")
def file_create(filename: str, content: str):
    """Create a file"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.create_file(filename, content)
            click.echo(result)

    asyncio.run(run())


@file.command("read")
@click.argument("filename")
def file_read(filename: str):
    """Read a file"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            content = await client.read_file(filename)
            click.echo(content)

    asyncio.run(run())


@file.command("delete")
@click.argument("filename")
def file_delete(filename: str):
    """Delete a file"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.delete_file(filename)
            click.echo(result)

    asyncio.run(run())


@file.command("list")
def file_list():
    """List all files"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.list_files()
            click.echo(result)

    asyncio.run(run())


# ========================================
# Calculator commands
# ========================================

@cli.group()
def calc():
    """Calculator commands"""
    pass


@calc.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def add(a: float, b: float):
    """Addition: a + b"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.calculate("add", a, b)
            click.echo(result)

    asyncio.run(run())


@calc.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def subtract(a: float, b: float):
    """Subtraction: a - b"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.calculate("subtract", a, b)
            click.echo(result)

    asyncio.run(run())


@calc.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def multiply(a: float, b: float):
    """Multiplication: a * b"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.calculate("multiply", a, b)
            click.echo(result)

    asyncio.run(run())


@calc.command()
@click.argument("a", type=float)
@click.argument("b", type=float)
def divide(a: float, b: float):
    """Division: a / b"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.calculate("divide", a, b)
            click.echo(result)

    asyncio.run(run())


@calc.command()
@click.argument("x", type=float)
def sqrt(x: float):
    """Square root: √x"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            result = await client.calculate("sqrt", x)
            click.echo(result)

    asyncio.run(run())


# ========================================
# Resource commands
# ========================================

@cli.command()
def list_resources():
    """List all resources"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            resources = await client.list_resources()
            if not resources:
                click.echo("No resources available")
                return

            click.echo("Available resources:")
            for res in resources:
                click.echo(f"  - {res.name}: {res.description}")
                click.echo(f"    URI: {res.uri}")

    asyncio.run(run())


@cli.command()
@click.argument("uri")
def read_resource(uri: str):
    """Read resource content"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            content = await client.read_resource(uri)
            click.echo(content)

    asyncio.run(run())


# ========================================
# Tool commands
# ========================================

@cli.command()
def list_tools():
    """List all tools"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            tools = await client.list_tools()
            if not tools:
                click.echo("No tools available")
                return

            click.echo("Available tools:")
            for tool in tools:
                click.echo(f"  - {tool.name}: {tool.description}")

    asyncio.run(run())


# ========================================
# Prompt commands
# ========================================

@cli.command()
def list_prompts():
    """List all prompts"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            prompts = await client.list_prompts()
            if not prompts:
                click.echo("No prompts available")
                return

            click.echo("Available prompts:")
            for prompt in prompts:
                click.echo(f"  - {prompt.name}: {prompt.description}")
                if prompt.arguments:
                    click.echo(f"    Arguments: {', '.join(arg.name for arg in prompt.arguments)}")

    asyncio.run(run())


@cli.command()
@click.argument("name")
@click.option("--language", "-l", help="Programming language (for code_review)")
def get_prompt(name: str, language: Optional[str]):
    """Get prompt content"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            args = {}
            if language:
                args["language"] = language

            prompt_text = await client.get_prompt(name, args)
            click.echo(prompt_text)

    asyncio.run(run())


# ========================================
# Info commands
# ========================================

@cli.command()
def info():
    """Show server information"""
    async def run():
        server_script = Path(__file__).parent / "server.py"
        async with mcp_client(server_script) as client:
            # Get various information
            tools = await client.list_tools()
            resources = await client.list_resources()
            prompts = await client.list_prompts()

            click.echo("=" * 50)
            click.echo("ToyMCP Server Information")
            click.echo("=" * 50)
            click.echo(f"Number of tools: {len(tools)}")
            click.echo(f"Number of resources: {len(resources)}")
            click.echo(f"Number of prompts: {len(prompts)}")
            click.echo()

            if tools:
                click.echo("Available tools:")
                for tool in tools:
                    click.echo(f"  - {tool.name}")

            if resources:
                click.echo("\nAvailable resources:")
                for res in resources:
                    click.echo(f"  - {res.name}")

            if prompts:
                click.echo("\nAvailable prompts:")
                for prompt in prompts:
                    click.echo(f"  - {prompt.name}")

    asyncio.run(run())


if __name__ == "__main__":
    cli()

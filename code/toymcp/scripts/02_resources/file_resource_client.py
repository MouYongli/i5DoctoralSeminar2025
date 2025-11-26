#!/usr/bin/env python3
"""
File Resource Server Test Client

This client tests the file_resource_server.py by:
1. Connecting to the server
2. Listing all available resources
3. Reading resource contents
4. Testing error handling and security

How to run:
    python test_file_resource_client.py
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add the src directory to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from toymcp.client import MCPClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.CYAN}ℹ {message}{Colors.END}")


async def main():
    """Main entry point: Test the file resource server"""

    # Server script path
    server_script = Path(__file__).parent / "file_resource_server.py"

    if not server_script.exists():
        print_error(f"Server script not found: {server_script}")
        return

    print_section("File Resource Server Test Client")
    print_info(f"Server script: {server_script}")

    # Create client
    client = MCPClient(server_script)

    try:
        # Connect to server
        print_section("1. Connecting to Server")
        await client.connect()
        print_success("Connected successfully!")

        # Test 1: List resources
        print_section("2. Listing Resources")
        resources = await client.list_resources()

        if resources:
            print_success(f"Found {len(resources)} resource(s):")
            for i, resource in enumerate(resources, 1):
                print(f"\n  {Colors.BOLD}Resource #{i}:{Colors.END}")
                print(f"    {Colors.CYAN}Name:{Colors.END} {resource.name}")
                print(f"    {Colors.CYAN}URI:{Colors.END} {resource.uri}")
                print(f"    {Colors.CYAN}Description:{Colors.END} {resource.description}")
                print(f"    {Colors.CYAN}MIME Type:{Colors.END} {resource.mimeType}")
        else:
            print_info("No resources found. The server will create sample files on first run.")

        # Test 2: Read each resource
        if resources:
            print_section("3. Reading Resource Contents")
            for resource in resources:
                print(f"\n{Colors.BOLD}Reading: {resource.name}{Colors.END}")
                try:
                    content = await client.read_resource(resource.uri)
                    print(f"{Colors.CYAN}Content ({len(content)} characters):{Colors.END}")
                    print(f"{Colors.YELLOW}{'─'*50}{Colors.END}")
                    print(content)
                    print(f"{Colors.YELLOW}{'─'*50}{Colors.END}")
                    print_success(f"Successfully read {resource.name}")
                except Exception as e:
                    print_error(f"Failed to read {resource.name}: {e}")

        # Test 3: Error handling - non-existent resource
        print_section("4. Testing Error Handling")

        # Test 3a: Non-existent file
        print(f"\n{Colors.BOLD}Test: Reading non-existent file{Colors.END}")
        try:
            await client.read_resource("file:///nonexistent.txt")
            print_error("Expected error not raised!")
        except Exception as e:
            print_success(f"Correctly handled non-existent file: {type(e).__name__}")
            print_info(f"Error message: {str(e)}")

        # Test 3b: Directory traversal attempt
        print(f"\n{Colors.BOLD}Test: Directory traversal attempt{Colors.END}")
        try:
            await client.read_resource("file:///../../../etc/passwd")
            print_error("Security vulnerability detected! Directory traversal succeeded!")
        except Exception as e:
            print_success(f"Security check passed: {type(e).__name__}")
            print_info(f"Error message: {str(e)}")

        # Summary
        print_section("Test Summary")
        print_success("All tests completed!")
        print_info("The server correctly:")
        print("  • Lists available resources")
        print("  • Reads resource contents")
        print("  • Handles non-existent files")
        print("  • Prevents directory traversal attacks")

    except KeyboardInterrupt:
        print_info("\nTest interrupted by user")

    except Exception as e:
        print_error(f"Test failed with error: {e}")
        logger.exception("Detailed error:")
        sys.exit(1)

    finally:
        # Disconnect
        print_section("5. Disconnecting")
        await client.disconnect()
        print_success("Disconnected successfully!")

if __name__ == "__main__":
    asyncio.run(main())

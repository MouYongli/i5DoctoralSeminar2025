#!/usr/bin/env python3
"""
Prompt template server example

This server provides a set of developer helper prompt templates to show:
1. How to define prompts and arguments
2. How to generate dynamic prompt content
3. How to customize prompts with arguments

Run:
    python prompt_template_server.py

Usage:
    Configure in Claude Desktop to use the predefined templates,
    e.g. choose the "code_review" prompt and enter language "Python".
"""

import asyncio
import logging
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, PromptArgument, GetPromptResult, PromptMessage, TextContent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger(__name__)

# Create server
app = Server("prompt-template-server")

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List all available prompt templates"""
    logger.info("Listing prompts")

    return [
        Prompt(
            name="code_review",
            description="Code review helper: assess code quality and find issues",
            arguments=[
                PromptArgument(
                    name="language",
                    description="Programming language (e.g., Python, JavaScript, Go)",
                    required=True
                ),
                PromptArgument(
                    name="focus",
                    description="Review focus (e.g., performance, security, readability), defaults to overall quality",
                    required=False
                )
            ]
        ),
        Prompt(
            name="debug_help",
            description="Debug helper: analyze and fix code errors",
            arguments=[
                PromptArgument(
                    name="error_type",
                    description="Error type (e.g., syntax, runtime, logic)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="write_tests",
            description="Test-writing helper: assist with unit tests",
            arguments=[
                PromptArgument(
                    name="framework",
                    description="Test framework (e.g., pytest, unittest, jest)",
                    required=False
                )
            ]
        ),
        Prompt(
            name="generate_docs",
            description="Docs helper: generate code documentation",
            arguments=[
                PromptArgument(
                    name="doc_type",
                    description="Documentation type: one of API, README, Tutorial",
                    required=True
                )
            ]
        ),
        Prompt(
            name="refactor_suggest",
            description="Refactoring suggestions helper",
            arguments=[]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Generate prompt content"""
    logger.info(f"Get prompt: {name}, args: {arguments}")

    if name == "code_review":
        language = arguments.get("language", "code")
        focus = arguments.get("focus", "overall quality")

        prompt_text = f"""As an experienced {language} developer, please review the code below.

Review focus: {focus}

Please provide:
1. Code quality score (0-10)
2. Issues and potential risks
3. Concrete improvement suggestions
4. Best practice recommendations

Paste the code to review below:
"""

        return GetPromptResult(
            description=f"{language} code review (focus: {focus})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "debug_help":
        error_type = arguments.get("error_type", "general error")

        prompt_text = f"""I'm facing a {error_type} and need help analyzing and fixing it.

Please provide:
1. Detailed analysis of the root cause
2. Potential solutions (ranked by recommendation)
3. Tips to avoid similar issues
4. Related debugging techniques and best practices

Paste the error details and related code:
"""

        return GetPromptResult(
            description=f"Debug helper: {error_type}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "write_tests":
        framework = arguments.get("framework", "standard test framework")

        prompt_text = f"""Please help write unit tests for the code below.

Test framework: {framework}

Requirements:
1. Cover primary functionality paths
2. Include edge case tests
3. Include exception handling tests
4. Keep test code clear and readable
5. Add necessary comments
6. Follow the AAA pattern (Arrange-Act-Assert)

Provide the code to test:
"""

        return GetPromptResult(
            description=f"Test-writing helper ({framework})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "generate_docs":
        doc_type = arguments.get("doc_type", "API")

        if doc_type == "API":
            prompt_text = """Please generate API documentation for the following code.

The docs should include:
1. Function/method descriptions
2. Parameter details (type, meaning, default)
3. Return value description
4. Usage examples
5. Caveats and limitations

Provide the code to document:
"""
        elif doc_type == "README":
            prompt_text = """Please generate a README.md for this project.

Include:
1. Project overview
2. Key features
3. Installation steps
4. Usage examples
5. Configuration notes
6. FAQ
7. Contribution guidelines

Provide project details:
"""
        elif doc_type == "Tutorial":
            prompt_text = """Please create a tutorial document.

The tutorial should cover:
1. Learning objectives
2. Prerequisites
3. Step-by-step guidance (with code examples)
4. Common errors and fixes
5. Advanced topics
6. Reference materials

Provide the tutorial topic and related info:
"""
        else:
            prompt_text = f"Please generate {doc_type} documentation."

        return GetPromptResult(
            description=f"{doc_type} documentation generation",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    elif name == "refactor_suggest":
        prompt_text = """Please analyze the code below and provide refactoring suggestions.

Your analysis should include:
1. Structural issues
2. Code smell detection
3. Suggested design patterns
4. Performance optimization opportunities
5. Maintainability improvements
6. Concrete refactoring steps

Provide the code to refactor:
"""

        return GetPromptResult(
            description="Code refactoring suggestions",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    else:
        logger.error(f"Unknown prompt: {name}")
        raise ValueError(f"Unknown prompt: {name}")

async def main():
    """Run the server"""
    logger.info("Starting prompt template server...")

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)

# Prompts (Templates)

## What Are Prompts?

Prompts are **predefined dialogue templates** served by an MCP server to help users interact with an LLM more efficiently.

### Characteristics

- **Structured**: predefined conversational flow  
- **Parameterized**: accept dynamic arguments  
- **Reusable**: best practices for common scenarios  
- **Guiding**: steer the LLM toward better outputs  

### Use Cases

- 📝 Code review templates  
- 🔍 Data analysis prompts  
- 🌐 Translation tasks  
- 📊 Report generation  
- 🧪 Test case authoring  
- 📖 Documentation guidance  

## Prompts vs Tools vs Resources

| Feature | Resources | Tools | Prompts |
|------|------|------|--------|
| Purpose | Provide data | Execute actions | Guide conversations |
| Executor | Server | Server | LLM |
| Side effects | None | Possible | None |
| Returns | Data content | Execution result | Prompt text |

## Prompt Structure

### 1. Prompt Definition

```python
{
  "name": "code_review",
  "description": "Code review prompt to assess code quality",
  "arguments": [
    {
      "name": "language",
      "description": "Programming language",
      "required": true
    },
    {
      "name": "focus",
      "description": "Review focus (e.g., performance, security, readability)",
      "required": false
    }
  ]
}
```

### 2. Prompt Request

Client invocation:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "prompts/get",
  "params": {
    "name": "code_review",
    "arguments": {
      "language": "Python",
      "focus": "Performance"
    }
  }
}
```

### 3. Prompt Response

Server returns the generated prompt content:

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "description": "Python code review (focus: Performance)",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Please review the following Python code with a focus on performance..."
        }
      }
    ]
  }
}
```

## Building a Prompt Server

### Core Methods

#### 1. List prompts (`prompts/list`)

```python
from mcp.types import Prompt, PromptArgument

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="code_review",
            description="Code review helper",
            arguments=[
                PromptArgument(
                    name="language",
                    description="Programming language",
                    required=True
                ),
                PromptArgument(
                    name="focus",
                    description="Review focus",
                    required=False
                )
            ]
        ),
        Prompt(
            name="translate",
            description="Translation helper",
            arguments=[
                PromptArgument(
                    name="source_lang",
                    description="Source language",
                    required=True
                ),
                PromptArgument(
                    name="target_lang",
                    description="Target language",
                    required=True
                )
            ]
        )
    ]
```

#### 2. Get prompt (`prompts/get`)

```python
from mcp.types import GetPromptResult, PromptMessage, TextContent

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "code_review":
        language = arguments.get("language", "code")
        focus = arguments.get("focus", "overall quality")

        prompt_text = f"""As an experienced {language} developer, please review the code below.

Review focus: {focus}

Provide:
1. Code quality assessment
2. Potential issues and risks
3. Improvement suggestions
4. Best practice recommendations

Paste the code here:
"""

        return GetPromptResult(
            description=f"{language} code review (focus: {focus})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=prompt_text
                    )
                )
            ]
        )

    elif name == "translate":
        source_lang = arguments["source_lang"]
        target_lang = arguments["target_lang"]

        prompt_text = f"""Please translate the following content from {source_lang} to {target_lang}.

Requirements:
- Preserve tone and style
- Translate technical terms accurately
- Keep original formatting

Provide the text to translate:
"""

        return GetPromptResult(
            description=f"Translation: {source_lang} → {target_lang}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )

    else:
        raise ValueError(f"Unknown prompt: {name}")
```

## Example: Developer Helper Prompts

A set of practical developer prompts.

### Features

- ✅ Code review (`code_review`)  
- ✅ Bug analysis (`debug_help`)  
- ✅ Documentation generation (`generate_docs`)  
- ✅ Test case authoring (`write_tests`)  
- ✅ Refactoring suggestions (`refactor_suggest`)  

### Full Implementation

```python
from mcp.server import Server
from mcp.types import Prompt, PromptArgument, GetPromptResult, PromptMessage, TextContent

app = Server("dev-prompts-server")

@app.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="code_review",
            description="Code review helper",
            arguments=[
                PromptArgument(name="language", description="Programming language", required=True),
                PromptArgument(name="focus", description="Review focus", required=False)
            ]
        ),
        Prompt(
            name="debug_help",
            description="Debugging helper",
            arguments=[
                PromptArgument(name="error_type", description="Error type", required=False)
            ]
        ),
        Prompt(
            name="generate_docs",
            description="Documentation helper",
            arguments=[
                PromptArgument(name="doc_type", description="Doc type (API/README/Tutorial)", required=True)
            ]
        ),
        Prompt(
            name="write_tests",
            description="Test case helper",
            arguments=[
                PromptArgument(name="framework", description="Test framework", required=False)
            ]
        )
    ]

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "debug_help":
        error_type = arguments.get("error_type", "general error")

        prompt_text = f"""I'm facing {error_type}; please help analyze and resolve it.

Please provide:
1. Root cause analysis
2. Possible solutions (ranked)
3. How to avoid similar issues
4. Relevant best practices

Error details and code:
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

        prompt_text = f"""Please write unit tests for the code below.

Test framework: {framework}

Requirements:
1. Cover main functionality paths
2. Include edge cases
3. Include exception handling
4. Keep tests clear and readable
5. Add necessary explanations

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

    # ... other prompts ...
```

### Full Example Code

See [scripts/04_prompts/prompt_template_server.py](../scripts/04_prompts/prompt_template_server.py).

## Advanced Prompt Techniques

### 1. Multi-turn prompts

```python
GetPromptResult(
    description="Refactoring guide",
    messages=[
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="I want to refactor this code to improve maintainability."
            )
        ),
        PromptMessage(
            role="assistant",
            content=TextContent(
                type="text",
                text="Sure, I'll analyze and suggest refactors. What are the main problems today?"
            )
        ),
        PromptMessage(
            role="user",
            content=TextContent(
                type="text",
                text="The code is too long and functions are unclear. Please analyze the following code:"
            )
        )
    ]
)
```

### 2. Include contextual resources

```python
from mcp.types import EmbeddedResource, Resource

@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "analyze_with_context":
        config_content = read_config_file()

        return GetPromptResult(
            description="Context-aware analysis",
            messages=[
                PromptMessage(
                    role="user",
                    content=[
                        TextContent(
                            type="text",
                            text="Analyze the code using the following config file:"
                        ),
                        EmbeddedResource(
                            type="resource",
                            resource=Resource(
                                uri="file:///config.json",
                                mimeType="application/json",
                                text=config_content
                            )
                        ),
                        TextContent(
                            type="text",
                            text="Here is the code:"
                        )
                    ]
                )
            ]
        )
```

### 3. Dynamic content

```python
@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "weekly_review":
        commits = await get_this_week_commits()
        issues = await get_this_week_issues()

        prompt_text = f"""Weekly summary

Commits: {len(commits)}
Issues handled: {len(issues)}

Commit details:
{format_commits(commits)}

Issue details:
{format_issues(issues)}

Please generate a professional weekly report covering:
1. Key work items
2. Major accomplishments
3. Challenges
4. Plans for next week
"""

        return GetPromptResult(
            description="Weekly summary",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )
```

### 4. Conditional prompts

```python
@app.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "smart_assistant":
        user_level = arguments.get("level", "beginner")

        if user_level == "beginner":
            prompt_text = "Use simple language and include detailed steps."
        elif user_level == "intermediate":
            prompt_text = "Provide standard solutions and best practices."
        else:  # advanced
            prompt_text = "Dive deep into technical details, performance tuning, and edge cases."

        return GetPromptResult(
            description=f"Smart assistant ({user_level} level)",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=prompt_text)
                )
            ]
        )
```

## Best Practices

### 1. Clear prompt descriptions

```python
# ❌ Vague
Prompt(name="helper", description="Help")

# ✅ Clear
Prompt(
    name="api_docs_generator",
    description="API docs generator: produces standardized API docs with parameter details, return values, and examples"
)
```

### 2. Thoughtful arguments

```python
# ✅ Provide defaults for guidance
PromptArgument(
    name="style",
    description="Documentation style (options: concise/detailed/technical), defaults to 'detailed'",
    required=False
)

# ✅ Restrict with enums
PromptArgument(
    name="format",
    description="Output format: markdown/html/pdf",
    required=True
)
```

### 3. Structured prompt text

```python
prompt_text = f"""# Task: {task_name}

## Goal
{objective}

## Requirements
1. {requirement_1}
2. {requirement_2}
3. {requirement_3}

## Input
Please provide:
- {input_1}
- {input_2}

## Expected Output
{expected_output_format}
"""
```

### 4. Include examples

```python
prompt_text = """Please write unit tests.

Example format:
```python
def test_example():
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_value
```

Write tests following the format above:
"""
```

## Using Prompts in Claude Desktop

### Configuration

```json
{
  "mcpServers": {
    "dev-prompts": {
      "command": "python",
      "args": ["scripts/04_prompts/prompt_template_server.py"]
    }
  }
}
```

### How to Use

Prompts appear in the Claude Desktop prompt picker:

1. Click the prompt icon  
2. Select "code_review"  
3. Fill parameters (language: "Python", focus: "Performance")  
4. Claude loads the prompt template  
5. Continue the conversation to finish the task  

## Testing Prompts

### Using Python Client

```python
async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()

        # List prompts
        prompts = await session.list_prompts()
        print(f"Available prompts: {prompts}")

        # Get prompt
        result = await session.get_prompt(
            "code_review",
            {"language": "Python", "focus": "Performance"}
        )

        print(f"Prompt: {result.messages[0].content.text}")
```

## Practical Prompt Examples

### Project initialization

```python
Prompt(
    name="init_project",
    description="Project bootstrapper: generate project structure, config files, README, etc.",
    arguments=[
        PromptArgument(name="project_type", description="Project type (web/api/cli/library)", required=True),
        PromptArgument(name="language", description="Primary programming language", required=True)
    ]
)
```

### Performance optimization

```python
Prompt(
    name="optimize_performance",
    description="Performance advisor: analyze bottlenecks and propose optimizations",
    arguments=[
        PromptArgument(name="metric", description="Target metric (speed/memory/concurrency)", required=True)
    ]
)
```

### Security audit

```python
Prompt(
    name="security_audit",
    description="Security audit helper: check for common issues (SQL injection, XSS, CSRF, etc.)",
    arguments=[
        PromptArgument(name="framework", description="Framework in use", required=False)
    ]
)
```

## Next Up

We’ve covered the three core MCP features: resources, tools, and prompts. Next, learn another transport: SSE.

Continue with [06_sse_transport.md](06_sse_transport.md).

## References

- [MCP Prompts spec](https://spec.modelcontextprotocol.io/specification/server/prompts/)  
- [Prompt type definitions](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/types.py)  
- [Prompt engineering best practices](https://docs.anthropic.com/claude/docs/prompt-engineering)  

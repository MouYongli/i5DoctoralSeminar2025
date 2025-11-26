import { NextRequest } from "next/server";

export async function POST(request: NextRequest) {
  const { messages } = await request.json();
  const lastMessage = messages[messages.length - 1];

  // Simulate AI response based on user input
  const response = generateMockResponse(lastMessage?.content || "");

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    async start(controller) {
      const words = response.split(" ");

      for (const word of words) {
        const data = JSON.stringify({ content: word + " " });
        controller.enqueue(encoder.encode(`data: ${data}\n\n`));
        // Simulate typing delay
        await new Promise((resolve) => setTimeout(resolve, 30 + Math.random() * 50));
      }

      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}

function generateMockResponse(input: string): string {
  const lowercased = input.toLowerCase();

  if (lowercased.includes("hello") || lowercased.includes("hi")) {
    return "Hello! I'm your AI assistant. I can help you with various tasks including answering questions, writing code, and explaining concepts. How can I assist you today?";
  }

  if (lowercased.includes("code") || lowercased.includes("function")) {
    return `Here's an example of a simple function:

\`\`\`typescript
function greet(name: string): string {
  return \`Hello, \${name}!\`;
}

// Usage
console.log(greet("World")); // Output: Hello, World!
\`\`\`

This function takes a name parameter and returns a greeting message. Feel free to ask if you need more complex examples!`;
  }

  if (lowercased.includes("workflow")) {
    return "Workflows allow you to orchestrate multiple AI agents and tools in a visual interface. You can:\n\n1. **Create nodes** - Add agent, tool, or condition nodes\n2. **Connect nodes** - Define the flow of data between nodes\n3. **Execute** - Run the workflow and see results\n\nWould you like me to explain any specific aspect of workflows?";
  }

  if (lowercased.includes("help")) {
    return "I can help you with:\n\n- **General questions** - Ask me anything!\n- **Code assistance** - Writing, reviewing, or explaining code\n- **Workflows** - Creating and managing AI agent workflows\n- **Documentation** - Understanding concepts and features\n\nWhat would you like to know more about?";
  }

  return `I understand you're asking about "${input.slice(0, 50)}${input.length > 50 ? "..." : ""}".

This is a demo response. In a production environment, this would connect to an actual AI model to provide intelligent responses.

Some things you can try:
- Say "hello" for a greeting
- Ask about "code" for a code example
- Ask about "workflows" to learn more
- Type "help" for assistance options`;
}

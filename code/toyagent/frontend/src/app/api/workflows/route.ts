import { NextRequest, NextResponse } from "next/server";

interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: unknown[];
  edges: unknown[];
  createdAt: string;
  updatedAt: string;
}

// Mock data store
const workflows = new Map<string, Workflow>();

// Initialize with demo workflow
workflows.set("demo", {
  id: "demo",
  name: "Demo Workflow",
  description: "A sample workflow demonstrating the capabilities",
  nodes: [
    {
      id: "1",
      type: "input",
      position: { x: 250, y: 50 },
      data: { label: "User Input", config: {} },
    },
    {
      id: "2",
      type: "agent",
      position: { x: 250, y: 150 },
      data: { label: "Classifier", config: { model: "gpt-4" } },
    },
  ],
  edges: [{ id: "e1-2", source: "1", target: "2" }],
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
});

export async function GET() {
  const list = Array.from(workflows.values()).sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  );
  return NextResponse.json(list);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const workflow: Workflow = {
    id: crypto.randomUUID(),
    name: body.name || "New Workflow",
    description: body.description,
    nodes: body.nodes || [],
    edges: body.edges || [],
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  workflows.set(workflow.id, workflow);
  return NextResponse.json(workflow, { status: 201 });
}

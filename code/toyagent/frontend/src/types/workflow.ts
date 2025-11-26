export type NodeType = "agent" | "tool" | "condition" | "input" | "output";

export interface WorkflowNodeData {
  label: string;
  config: Record<string, unknown>;
}

export interface WorkflowNode {
  id: string;
  type: NodeType;
  position: { x: number; y: number };
  data: WorkflowNodeData;
}

export interface WorkflowEdge {
  id: string;
  source: string;
  target: string;
  sourceHandle?: string;
  targetHandle?: string;
  label?: string;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  createdAt: Date;
  updatedAt: Date;
}

export type ExecutionStatus = "pending" | "running" | "completed" | "error";

export interface ExecutionStep {
  id: string;
  nodeId: string;
  nodeName: string;
  status: ExecutionStatus;
  input?: unknown;
  output?: unknown;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: ExecutionStatus;
  steps: ExecutionStep[];
  startedAt: Date;
  completedAt?: Date;
}

"use client";

import { useCallback, useMemo, useState, useEffect } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  BackgroundVariant,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Save, Play, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { NodePalette } from "./NodePalette";
import {
  AgentNode,
  ToolNode,
  ConditionNode,
  InputNode,
  OutputNode,
} from "./nodes";
import { useWorkflowStore } from "@/stores";

interface WorkflowCanvasProps {
  workflowId: string;
  readOnly?: boolean;
}

const nodeTypes = {
  agent: AgentNode,
  tool: ToolNode,
  condition: ConditionNode,
  input: InputNode,
  output: OutputNode,
};

// Demo workflow data
const demoNodes: Node[] = [
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
  {
    id: "3",
    type: "condition",
    position: { x: 250, y: 270 },
    data: { label: "Is Question?", config: {} },
  },
  {
    id: "4",
    type: "agent",
    position: { x: 100, y: 400 },
    data: { label: "Answer Agent", config: { model: "gpt-4" } },
  },
  {
    id: "5",
    type: "tool",
    position: { x: 400, y: 400 },
    data: { label: "Search", config: { toolName: "web_search" } },
  },
  {
    id: "6",
    type: "output",
    position: { x: 250, y: 530 },
    data: { label: "Response", config: {} },
  },
];

const demoEdges: Edge[] = [
  { id: "e1-2", source: "1", target: "2" },
  { id: "e2-3", source: "2", target: "3" },
  { id: "e3-4", source: "3", target: "4", sourceHandle: "true" },
  { id: "e3-5", source: "3", target: "5", sourceHandle: "false" },
  { id: "e4-6", source: "4", target: "6" },
  { id: "e5-6", source: "5", target: "6" },
];

export function WorkflowCanvas({ workflowId, readOnly = false }: WorkflowCanvasProps) {
  const { isAdmin } = useWorkflowStore();
  const [nodes, setNodes, onNodesChange] = useNodesState(demoNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(demoEdges);
  const [workflowName, setWorkflowName] = useState("Demo Workflow");

  const isEditMode = !readOnly && isAdmin;

  // Load workflow data
  useEffect(() => {
    if (workflowId === "new") {
      setNodes([]);
      setEdges([]);
      setWorkflowName("New Workflow");
    }
    // TODO: Load workflow from API
  }, [workflowId, setNodes, setEdges]);

  const onConnect = useCallback(
    (connection: Connection) => {
      if (isEditMode) {
        setEdges((eds) => addEdge(connection, eds));
      }
    },
    [isEditMode, setEdges]
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!isEditMode) return;

      const type = event.dataTransfer.getData("application/reactflow/type");
      const label = event.dataTransfer.getData("application/reactflow/label");

      if (!type) return;

      const position = {
        x: event.clientX - 300,
        y: event.clientY - 100,
      };

      const newNode: Node = {
        id: crypto.randomUUID(),
        type,
        position,
        data: { label, config: {} },
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [isEditMode, setNodes]
  );

  const handleDragStart = useCallback(
    (event: React.DragEvent, nodeType: string, label: string) => {
      event.dataTransfer.setData("application/reactflow/type", nodeType);
      event.dataTransfer.setData("application/reactflow/label", label);
      event.dataTransfer.effectAllowed = "move";
    },
    []
  );

  const handleSave = useCallback(() => {
    console.log("Saving workflow:", { nodes, edges });
    // TODO: Save to API
  }, [nodes, edges]);

  const handleRun = useCallback(() => {
    console.log("Running workflow");
    // TODO: Execute workflow
  }, []);

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="flex h-full">
      <div className="flex flex-1 flex-col">
        {/* Toolbar */}
        <div className="flex items-center justify-between border-b bg-card px-4 py-2">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/workflows">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Link>
            </Button>
            <input
              type="text"
              value={workflowName}
              onChange={(e) => isEditMode && setWorkflowName(e.target.value)}
              readOnly={!isEditMode}
              className="border-none bg-transparent text-lg font-semibold outline-none focus:ring-0"
            />
          </div>
          <div className="flex items-center gap-2">
            {isEditMode && (
              <Button variant="outline" size="sm" onClick={handleSave}>
                <Save className="mr-2 h-4 w-4" />
                Save
              </Button>
            )}
            <Button size="sm" onClick={handleRun}>
              <Play className="mr-2 h-4 w-4" />
              Run
            </Button>
          </div>
        </div>

        {/* Canvas */}
        <div className="flex-1">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={isEditMode ? onNodesChange : undefined}
            onEdgesChange={isEditMode ? onEdgesChange : undefined}
            onConnect={onConnect}
            onDragOver={onDragOver}
            onDrop={onDrop}
            nodeTypes={nodeTypes}
            proOptions={proOptions}
            fitView
            deleteKeyCode={isEditMode ? ["Backspace", "Delete"] : []}
            nodesDraggable={isEditMode}
            nodesConnectable={isEditMode}
            elementsSelectable={isEditMode}
          >
            <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
            <Controls showInteractive={false} />
            <MiniMap
              nodeColor={(node) => {
                switch (node.type) {
                  case "agent":
                    return "#3b82f6";
                  case "tool":
                    return "#22c55e";
                  case "condition":
                    return "#eab308";
                  default:
                    return "#6b7280";
                }
              }}
            />
          </ReactFlow>
        </div>
      </div>

      {/* Node Palette - only in edit mode */}
      {isEditMode && <NodePalette onDragStart={handleDragStart} />}
    </div>
  );
}

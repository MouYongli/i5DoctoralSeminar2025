"use client";

import { Bot, Wrench, GitBranch, ArrowRight, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface NodePaletteProps {
  onDragStart: (
    event: React.DragEvent,
    nodeType: string,
    label: string
  ) => void;
}

const nodeTypes = [
  {
    type: "input",
    label: "Input",
    icon: ArrowRight,
    description: "Start of workflow",
    color: "text-primary bg-primary/10",
  },
  {
    type: "agent",
    label: "Agent",
    icon: Bot,
    description: "AI Agent node",
    color: "text-blue-600 bg-blue-100 dark:text-blue-400 dark:bg-blue-900",
  },
  {
    type: "tool",
    label: "Tool",
    icon: Wrench,
    description: "External tool call",
    color: "text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900",
  },
  {
    type: "condition",
    label: "Condition",
    icon: GitBranch,
    description: "Branch logic",
    color:
      "text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900",
  },
  {
    type: "output",
    label: "Output",
    icon: ArrowLeft,
    description: "End of workflow",
    color: "text-primary bg-primary/10",
  },
];

export function NodePalette({ onDragStart }: NodePaletteProps) {
  return (
    <div className="w-64 border-l bg-card p-4">
      <h3 className="mb-4 text-sm font-medium">Components</h3>
      <div className="space-y-2">
        {nodeTypes.map((node) => (
          <div
            key={node.type}
            draggable
            onDragStart={(e) => onDragStart(e, node.type, node.label)}
            className={cn(
              "flex cursor-grab items-center gap-3 rounded-lg border p-3 transition-colors",
              "hover:border-primary/50 hover:bg-accent active:cursor-grabbing"
            )}
          >
            <div
              className={cn(
                "flex h-8 w-8 items-center justify-center rounded-md",
                node.color
              )}
            >
              <node.icon className="h-4 w-4" />
            </div>
            <div className="min-w-0 flex-1">
              <div className="text-sm font-medium">{node.label}</div>
              <div className="truncate text-xs text-muted-foreground">
                {node.description}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

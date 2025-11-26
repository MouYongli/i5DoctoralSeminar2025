"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Plus, GitBranch, Shield, ShieldOff } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useWorkflowStore } from "@/stores";
import type { Workflow } from "@/types";

// Demo workflow data
const demoWorkflows: Workflow[] = [
  {
    id: "demo-1",
    name: "Question Answering",
    description: "Classifies user input and routes to appropriate handler",
    nodes: [
      { id: "1", type: "input", position: { x: 0, y: 0 }, data: { label: "Input", config: {} } },
      { id: "2", type: "agent", position: { x: 0, y: 100 }, data: { label: "Classifier", config: { model: "gpt-4" } } },
      { id: "3", type: "condition", position: { x: 0, y: 200 }, data: { label: "Is Question?", config: {} } },
      { id: "4", type: "agent", position: { x: -100, y: 300 }, data: { label: "Answer", config: {} } },
      { id: "5", type: "tool", position: { x: 100, y: 300 }, data: { label: "Search", config: {} } },
      { id: "6", type: "output", position: { x: 0, y: 400 }, data: { label: "Output", config: {} } },
    ],
    edges: [
      { id: "e1-2", source: "1", target: "2" },
      { id: "e2-3", source: "2", target: "3" },
      { id: "e3-4", source: "3", target: "4", sourceHandle: "true" },
      { id: "e3-5", source: "3", target: "5", sourceHandle: "false" },
      { id: "e4-6", source: "4", target: "6" },
      { id: "e5-6", source: "5", target: "6" },
    ],
    createdAt: new Date(),
    updatedAt: new Date(),
  },
  {
    id: "demo-2",
    name: "Code Review",
    description: "Automated code review workflow with multiple agents",
    nodes: [
      { id: "1", type: "input", position: { x: 0, y: 0 }, data: { label: "Code Input", config: {} } },
      { id: "2", type: "agent", position: { x: 0, y: 100 }, data: { label: "Analyzer", config: {} } },
      { id: "3", type: "output", position: { x: 0, y: 200 }, data: { label: "Review", config: {} } },
    ],
    edges: [
      { id: "e1-2", source: "1", target: "2" },
      { id: "e2-3", source: "2", target: "3" },
    ],
    createdAt: new Date(),
    updatedAt: new Date(),
  },
];

export default function WorkflowsPage() {
  const { workflows, isAdmin, setWorkflows, setAdmin } = useWorkflowStore();

  // Initialize demo workflows
  useEffect(() => {
    if (workflows.length === 0) {
      setWorkflows(demoWorkflows);
    }
  }, [workflows.length, setWorkflows]);

  return (
    <div className="p-6">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold">Workflows</h2>
          <p className="text-sm text-muted-foreground">
            Manage and view AI agent workflows
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={isAdmin ? "default" : "outline"}
            size="sm"
            onClick={() => setAdmin(!isAdmin)}
          >
            {isAdmin ? (
              <>
                <Shield className="mr-2 h-4 w-4" />
                Admin Mode
              </>
            ) : (
              <>
                <ShieldOff className="mr-2 h-4 w-4" />
                View Mode
              </>
            )}
          </Button>
          {isAdmin && (
            <Button asChild>
              <Link href="/workflows/new/edit">
                <Plus className="mr-2 h-4 w-4" />
                New Workflow
              </Link>
            </Button>
          )}
        </div>
      </div>

      {workflows.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-12">
          <GitBranch className="mb-4 h-12 w-12 text-muted-foreground" />
          <h3 className="mb-2 text-lg font-medium">No workflows yet</h3>
          <p className="mb-4 text-sm text-muted-foreground">
            {isAdmin
              ? "Create your first workflow to get started"
              : "No workflows available"}
          </p>
          {isAdmin && (
            <Button asChild>
              <Link href="/workflows/new/edit">
                <Plus className="mr-2 h-4 w-4" />
                Create Workflow
              </Link>
            </Button>
          )}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {workflows.map((workflow) => (
            <Link
              key={workflow.id}
              href={isAdmin ? `/workflows/${workflow.id}/edit` : `/workflows/${workflow.id}`}
              className="group rounded-lg border p-4 transition-colors hover:bg-accent"
            >
              <div className="mb-2 flex items-center gap-2">
                <GitBranch className="h-5 w-5 text-muted-foreground" />
                <h3 className="font-medium group-hover:text-accent-foreground">
                  {workflow.name}
                </h3>
              </div>
              {workflow.description && (
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {workflow.description}
                </p>
              )}
              <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
                <span>{workflow.nodes.length} nodes</span>
                <span>·</span>
                <span>{workflow.edges.length} connections</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

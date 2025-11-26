"use client";

import { useEffect, useState } from "react";
import type { WorkflowMeta, WorkflowStatus as WorkflowStatusType } from "@/types";
import { streamWorkflowStatus, getWorkflowResult } from "@/lib/api";
import { CheckCircle2, Circle, AlertCircle, Loader2, Play } from "lucide-react";

interface WorkflowStatusProps {
  workflow: WorkflowMeta;
}

type StepStatus = "pending" | "running" | "completed" | "failed";

interface StepState {
  id: string;
  title: string;
  status: StepStatus;
}

export function WorkflowStatus({ workflow }: WorkflowStatusProps) {
  const [steps, setSteps] = useState<StepState[]>(() =>
    workflow.spec.steps.map((step) => ({
      id: step.id,
      title: step.title,
      status: (workflow.steps_status[step.id] as StepStatus) || "pending",
    }))
  );
  const [overallStatus, setOverallStatus] = useState(workflow.status);
  const [isExpanded, setIsExpanded] = useState(true);

  useEffect(() => {
    if (overallStatus === "completed" || overallStatus === "failed") return;

    const abortController = new AbortController();

    streamWorkflowStatus(workflow.id, {
      onStepStart: (stepId) => {
        setSteps((prev) =>
          prev.map((s) => (s.id === stepId ? { ...s, status: "running" } : s))
        );
      },
      onStepProgress: (stepId, status) => {
        setSteps((prev) =>
          prev.map((s) =>
            s.id === stepId ? { ...s, status: status as StepStatus } : s
          )
        );
      },
      onStepComplete: (stepId) => {
        setSteps((prev) =>
          prev.map((s) => (s.id === stepId ? { ...s, status: "completed" } : s))
        );
      },
      onStepFailed: (stepId) => {
        setSteps((prev) =>
          prev.map((s) => (s.id === stepId ? { ...s, status: "failed" } : s))
        );
      },
      onWorkflowComplete: () => {
        setOverallStatus("completed");
      },
      onWorkflowFailed: () => {
        setOverallStatus("failed");
      },
      onError: (error) => {
        console.error("Workflow stream error:", error);
      },
    });

    return () => {
      abortController.abort();
    };
  }, [workflow.id, overallStatus]);

  const getStatusIcon = (status: StepStatus) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-blue-500" />;
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Circle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getOverallStatusColor = () => {
    switch (overallStatus) {
      case "completed":
        return "text-green-600 bg-green-50 dark:bg-green-900/20";
      case "running":
        return "text-blue-600 bg-blue-50 dark:bg-blue-900/20";
      case "failed":
        return "text-red-600 bg-red-50 dark:bg-red-900/20";
      default:
        return "text-muted-foreground bg-muted";
    }
  };

  return (
    <div className="rounded-lg border bg-card p-3">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex w-full items-center justify-between"
      >
        <div className="flex items-center gap-2">
          <Play className="h-4 w-4" />
          <span className="font-medium">{workflow.name}</span>
        </div>
        <span
          className={`rounded-full px-2 py-0.5 text-xs font-medium ${getOverallStatusColor()}`}
        >
          {overallStatus}
        </span>
      </button>

      {isExpanded && (
        <div className="mt-3 space-y-2">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                {getStatusIcon(step.status)}
                <span className="text-xs text-muted-foreground">
                  {index + 1}.
                </span>
              </div>
              <span
                className={`text-sm ${
                  step.status === "completed"
                    ? "text-muted-foreground line-through"
                    : step.status === "running"
                    ? "font-medium"
                    : ""
                }`}
              >
                {step.title}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

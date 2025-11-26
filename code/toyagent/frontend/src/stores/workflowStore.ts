import { create } from "zustand";
import type { Workflow, WorkflowExecution, ExecutionStep } from "@/types";

interface WorkflowState {
  workflows: Workflow[];
  currentWorkflow: Workflow | null;
  execution: WorkflowExecution | null;
  isAdmin: boolean;
  isLoading: boolean;

  // Actions
  setWorkflows: (workflows: Workflow[]) => void;
  setCurrentWorkflow: (workflow: Workflow | null) => void;
  addWorkflow: (workflow: Workflow) => void;
  updateWorkflow: (id: string, updates: Partial<Workflow>) => void;
  deleteWorkflow: (id: string) => void;

  setExecution: (execution: WorkflowExecution | null) => void;
  updateExecutionStep: (stepId: string, updates: Partial<ExecutionStep>) => void;

  setAdmin: (isAdmin: boolean) => void;
  setLoading: (loading: boolean) => void;
}

export const useWorkflowStore = create<WorkflowState>((set) => ({
  workflows: [],
  currentWorkflow: null,
  execution: null,
  isAdmin: false,
  isLoading: false,

  setWorkflows: (workflows) => set({ workflows }),

  setCurrentWorkflow: (workflow) => set({ currentWorkflow: workflow }),

  addWorkflow: (workflow) =>
    set((state) => ({
      workflows: [workflow, ...state.workflows],
    })),

  updateWorkflow: (id, updates) =>
    set((state) => ({
      workflows: state.workflows.map((w) =>
        w.id === id ? { ...w, ...updates } : w
      ),
      currentWorkflow:
        state.currentWorkflow?.id === id
          ? { ...state.currentWorkflow, ...updates }
          : state.currentWorkflow,
    })),

  deleteWorkflow: (id) =>
    set((state) => ({
      workflows: state.workflows.filter((w) => w.id !== id),
      currentWorkflow:
        state.currentWorkflow?.id === id ? null : state.currentWorkflow,
    })),

  setExecution: (execution) => set({ execution }),

  updateExecutionStep: (stepId, updates) =>
    set((state) => {
      if (!state.execution) return state;
      return {
        execution: {
          ...state.execution,
          steps: state.execution.steps.map((s) =>
            s.id === stepId ? { ...s, ...updates } : s
          ),
        },
      };
    }),

  setAdmin: (isAdmin) => set({ isAdmin }),
  setLoading: (isLoading) => set({ isLoading }),
}));

"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { GitBranch } from "lucide-react";
import { cn } from "@/lib/utils";

interface ConditionNodeData {
  label: string;
  config: {
    condition?: string;
  };
}

export const ConditionNode = memo(function ConditionNode({
  data,
  selected,
}: NodeProps & { data: ConditionNodeData }) {
  return (
    <div
      className={cn(
        "min-w-[150px] rounded-lg border bg-card p-3 shadow-sm transition-shadow",
        selected && "ring-2 ring-ring"
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3 !w-3 !border-2 !border-background !bg-primary"
      />
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-yellow-100 dark:bg-yellow-900">
          <GitBranch className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium">{data.label}</div>
          <div className="truncate text-xs text-muted-foreground">Condition</div>
        </div>
      </div>
      <div className="mt-2 flex justify-between">
        <Handle
          type="source"
          position={Position.Bottom}
          id="true"
          className="!relative !left-auto !top-auto !h-3 !w-3 !translate-x-0 !translate-y-0 !border-2 !border-background !bg-green-500"
        />
        <Handle
          type="source"
          position={Position.Bottom}
          id="false"
          className="!relative !left-auto !top-auto !h-3 !w-3 !translate-x-0 !translate-y-0 !border-2 !border-background !bg-red-500"
        />
      </div>
    </div>
  );
});

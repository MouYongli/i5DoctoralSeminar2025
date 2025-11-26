"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Wrench } from "lucide-react";
import { cn } from "@/lib/utils";

interface ToolNodeData {
  label: string;
  config: {
    toolName?: string;
    parameters?: Record<string, unknown>;
  };
}

export const ToolNode = memo(function ToolNode({
  data,
  selected,
}: NodeProps & { data: ToolNodeData }) {
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
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-green-100 dark:bg-green-900">
          <Wrench className="h-4 w-4 text-green-600 dark:text-green-400" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium">{data.label}</div>
          {data.config.toolName && (
            <div className="truncate text-xs text-muted-foreground">
              {data.config.toolName}
            </div>
          )}
        </div>
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-3 !w-3 !border-2 !border-background !bg-primary"
      />
    </div>
  );
});

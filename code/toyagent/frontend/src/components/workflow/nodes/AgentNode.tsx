"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { Bot } from "lucide-react";
import { cn } from "@/lib/utils";

interface AgentNodeData {
  label: string;
  config: {
    model?: string;
    systemPrompt?: string;
  };
}

export const AgentNode = memo(function AgentNode({
  data,
  selected,
}: NodeProps & { data: AgentNodeData }) {
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
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-blue-100 dark:bg-blue-900">
          <Bot className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="truncate text-sm font-medium">{data.label}</div>
          {data.config.model && (
            <div className="truncate text-xs text-muted-foreground">
              {data.config.model}
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

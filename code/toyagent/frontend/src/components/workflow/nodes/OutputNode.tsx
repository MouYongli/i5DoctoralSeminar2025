"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

interface OutputNodeData {
  label: string;
  config: Record<string, unknown>;
}

export const OutputNode = memo(function OutputNode({
  data,
  selected,
}: NodeProps & { data: OutputNodeData }) {
  return (
    <div
      className={cn(
        "min-w-[120px] rounded-lg border-2 border-dashed border-primary/50 bg-card p-3 shadow-sm transition-shadow",
        selected && "ring-2 ring-ring"
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-3 !w-3 !border-2 !border-background !bg-primary"
      />
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
          <ArrowLeft className="h-4 w-4 text-primary" />
        </div>
        <div className="text-sm font-medium">{data.label}</div>
      </div>
    </div>
  );
});

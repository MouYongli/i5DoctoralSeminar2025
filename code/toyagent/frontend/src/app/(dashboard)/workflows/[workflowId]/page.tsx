"use client";

import { use } from "react";
import { WorkflowCanvas } from "@/components/workflow/WorkflowCanvas";

export default function WorkflowViewPage({
  params,
}: {
  params: Promise<{ workflowId: string }>;
}) {
  const { workflowId } = use(params);

  return <WorkflowCanvas workflowId={workflowId} readOnly />;
}

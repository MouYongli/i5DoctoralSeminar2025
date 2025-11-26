/**
 * API client for ToyAgent backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Types matching backend schema
export interface Chat {
  id: string;
  title: string;
  context: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
  workflows: WorkflowMeta[];
}

export interface ChatListItem {
  id: string;
  title: string;
  context: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface ChatMessage {
  id: string;
  chat_id: string;
  sender: "user" | "agent" | "system";
  content: string;
  related_workflow_id: string | null;
  created_at: string;
}

export interface WorkflowMeta {
  id: string;
  chat_id: string;
  temporal_workflow_id: string;
  name: string;
  status: "pending" | "running" | "completed" | "failed";
  spec: WorkflowSpec;
  steps_status: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface WorkflowSpec {
  name: string;
  version: string;
  steps: WorkflowStep[];
}

export interface WorkflowStep {
  id: string;
  type: "tool" | "llm" | "condition" | "parallel";
  title: string;
  input: Record<string, unknown>;
  uses?: string;
  output_key?: string;
}

export interface ChatResponse {
  user_message: ChatMessage;
  agent_message: ChatMessage;
  workflow: WorkflowMeta | null;
}

// API functions
export async function createChat(title: string): Promise<Chat> {
  const response = await fetch(`${API_BASE_URL}/chats`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!response.ok) throw new Error("Failed to create chat");
  return response.json();
}

export async function listChats(): Promise<ChatListItem[]> {
  const response = await fetch(`${API_BASE_URL}/chats`);
  if (!response.ok) throw new Error("Failed to list chats");
  return response.json();
}

export async function getChat(chatId: string): Promise<Chat> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}`);
  if (!response.ok) throw new Error("Failed to get chat");
  return response.json();
}

export async function deleteChat(chatId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete chat");
}

export async function sendMessage(
  chatId: string,
  content: string
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chats/${chatId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ content }),
  });
  if (!response.ok) throw new Error("Failed to send message");
  return response.json();
}

// SSE Streaming functions
export interface StreamCallbacks {
  onMessageStart?: (type: "user" | "agent", messageId?: string) => void;
  onContentDelta?: (content: string) => void;
  onMessageEnd?: (messageId: string, hasWorkflow: boolean) => void;
  onWorkflowCreated?: (workflow: WorkflowMeta) => void;
  onError?: (error: string) => void;
}

export async function sendMessageStream(
  chatId: string,
  content: string,
  callbacks: StreamCallbacks
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/stream/chats/${chatId}/stream`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "text/event-stream",
      },
      body: JSON.stringify({ content }),
    }
  );

  if (!response.ok) {
    callbacks.onError?.(`HTTP error: ${response.status}`);
    return;
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    callbacks.onError?.("No response body");
    return;
  }

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("event: ")) {
        // Skip event line, will be parsed with data
        continue;
      }
      if (line.startsWith("data: ")) {
        try {
          // Handle nested data format from sse-starlette
          let dataStr = line.slice(6);

          // Check if it's an event line embedded in data
          if (dataStr.startsWith("event: ")) {
            continue;
          }
          if (dataStr.startsWith("data: ")) {
            dataStr = dataStr.slice(6);
          }

          if (!dataStr.trim()) continue;

          const data = JSON.parse(dataStr);

          // Handle different event types based on data content
          if (data.type === "user" || data.type === "agent") {
            callbacks.onMessageStart?.(data.type, data.message_id);
          } else if (data.content !== undefined) {
            callbacks.onContentDelta?.(data.content);
          } else if (data.message_id && data.has_workflow !== undefined) {
            callbacks.onMessageEnd?.(data.message_id, data.has_workflow);
          } else if (data.temporal_workflow_id) {
            callbacks.onWorkflowCreated?.(data as WorkflowMeta);
          } else if (data.error) {
            callbacks.onError?.(data.error);
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }
}

// Workflow API functions
export async function getWorkflow(workflowId: string): Promise<WorkflowMeta> {
  const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}`);
  if (!response.ok) throw new Error("Failed to get workflow");
  return response.json();
}

export interface WorkflowStatus {
  workflow_id: string;
  temporal_workflow_id: string;
  status: string;
  current_step: string | null;
  step_statuses: Record<string, string>;
}

export async function getWorkflowStatus(
  workflowId: string
): Promise<WorkflowStatus> {
  const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/status`);
  if (!response.ok) throw new Error("Failed to get workflow status");
  return response.json();
}

export interface WorkflowResult {
  workflow_id: string;
  temporal_workflow_id: string;
  success: boolean;
  results: Record<string, unknown>;
  step_statuses: Record<string, string>;
  error?: string;
}

export async function getWorkflowResult(
  workflowId: string
): Promise<WorkflowResult> {
  const response = await fetch(`${API_BASE_URL}/workflows/${workflowId}/result`);
  if (!response.ok) throw new Error("Failed to get workflow result");
  return response.json();
}

// Workflow SSE streaming
export interface WorkflowStreamCallbacks {
  onWorkflowStart?: (workflowId: string, name: string, status: string) => void;
  onStepStart?: (stepId: string, status: string) => void;
  onStepProgress?: (stepId: string, status: string) => void;
  onStepComplete?: (stepId: string) => void;
  onStepFailed?: (stepId: string) => void;
  onWorkflowComplete?: (
    workflowId: string,
    stepStatuses: Record<string, string>
  ) => void;
  onWorkflowFailed?: (
    workflowId: string,
    stepStatuses: Record<string, string>
  ) => void;
  onError?: (error: string) => void;
}

export async function streamWorkflowStatus(
  workflowId: string,
  callbacks: WorkflowStreamCallbacks
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/stream/workflows/${workflowId}/stream`,
    {
      headers: { Accept: "text/event-stream" },
    }
  );

  if (!response.ok) {
    callbacks.onError?.(`HTTP error: ${response.status}`);
    return;
  }

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  if (!reader) {
    callbacks.onError?.("No response body");
    return;
  }

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        try {
          let dataStr = line.slice(6);
          if (dataStr.startsWith("data: ")) {
            dataStr = dataStr.slice(6);
          }
          if (!dataStr.trim()) continue;

          const data = JSON.parse(dataStr);

          if (data.name && data.status) {
            callbacks.onWorkflowStart?.(data.workflow_id, data.name, data.status);
          } else if (data.step_id) {
            if (data.status === "running") {
              callbacks.onStepStart?.(data.step_id, data.status);
            } else if (data.status) {
              callbacks.onStepProgress?.(data.step_id, data.status);
            }
          }
        } catch {
          // Ignore parse errors
        }
      }
    }
  }
}

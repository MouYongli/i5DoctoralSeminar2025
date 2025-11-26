// Types matching backend API schema (from lib/api.ts)
export type {
  Chat,
  ChatListItem,
  ChatMessage,
  WorkflowMeta,
  WorkflowSpec,
  WorkflowStep,
  ChatResponse,
  WorkflowStatus,
  WorkflowResult,
} from "@/lib/api";

// Simplified types for UI components
export interface Message {
  id: string;
  chatId: string;
  role: "user" | "assistant" | "system";
  content: string;
  createdAt: Date;
  workflowId?: string | null;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

// Convert API types to UI types
export function toMessage(msg: import("@/lib/api").ChatMessage): Message {
  return {
    id: msg.id,
    chatId: msg.chat_id,
    role: msg.sender === "agent" ? "assistant" : msg.sender,
    content: msg.content,
    createdAt: new Date(msg.created_at),
    workflowId: msg.related_workflow_id,
  };
}

export function toConversation(chat: import("@/lib/api").ChatListItem): Conversation {
  return {
    id: chat.id,
    title: chat.title,
    createdAt: new Date(chat.created_at),
    updatedAt: new Date(chat.updated_at),
    messageCount: chat.message_count,
  };
}

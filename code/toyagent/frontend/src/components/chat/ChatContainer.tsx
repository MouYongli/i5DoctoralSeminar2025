"use client";

import { useEffect } from "react";
import { useChatStore } from "@/stores";
import { MessageList } from "./MessageList";
import { ChatInput } from "./ChatInput";
import { WorkflowStatus } from "../workflow/WorkflowStatus";

interface ChatContainerProps {
  chatId?: string;
}

export function ChatContainer({ chatId }: ChatContainerProps) {
  const {
    messages,
    isStreaming,
    isLoading,
    error,
    currentWorkflow,
    loadChat,
    sendMessage,
    setMessages,
    setCurrentChatId,
    setCurrentWorkflow,
  } = useChatStore();

  // Load chat when chatId changes
  useEffect(() => {
    if (chatId) {
      loadChat(chatId);
    } else {
      setMessages([]);
      setCurrentChatId(null);
      setCurrentWorkflow(null);
    }
  }, [chatId, loadChat, setMessages, setCurrentChatId, setCurrentWorkflow]);

  const handleSend = async (content: string) => {
    await sendMessage(content);
  };

  return (
    <div className="flex h-full flex-col">
      {error && (
        <div className="mx-4 mt-2 rounded-md bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
          {error}
        </div>
      )}

      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        isLoading={isLoading}
      />

      {currentWorkflow && (
        <div className="border-t border-border px-4 py-2">
          <WorkflowStatus workflow={currentWorkflow} />
        </div>
      )}

      <ChatInput onSend={handleSend} disabled={isStreaming || isLoading} />
    </div>
  );
}

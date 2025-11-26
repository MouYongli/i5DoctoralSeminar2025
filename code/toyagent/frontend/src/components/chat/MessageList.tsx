"use client";

import { useEffect, useRef } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { MessageItem } from "./MessageItem";
import type { Message } from "@/types";

interface MessageListProps {
  messages: Message[];
  isStreaming?: boolean;
  isLoading?: boolean;
}

export function MessageList({ messages, isStreaming, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  if (isLoading) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="flex items-center gap-2 text-muted-foreground">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          <span>Loading conversation...</span>
        </div>
      </div>
    );
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-1 items-center justify-center">
        <div className="text-center">
          <h2 className="mb-2 text-xl font-semibold">ToyAgent Assistant</h2>
          <p className="text-muted-foreground">
            Start a conversation by typing a message below
          </p>
        </div>
      </div>
    );
  }

  return (
    <ScrollArea className="flex-1">
      <div className="divide-y">
        {messages.map((message) => (
          <MessageItem key={message.id} message={message} />
        ))}
      </div>
      {isStreaming && (
        <div className="flex gap-4 bg-muted/30 px-4 py-6">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary">
            <span className="h-2 w-2 animate-pulse rounded-full bg-foreground" />
          </div>
          <div className="flex items-center">
            <span className="text-sm text-muted-foreground">Thinking...</span>
          </div>
        </div>
      )}
      <div ref={bottomRef} />
    </ScrollArea>
  );
}

"use client";

import { Bot, User, Workflow } from "lucide-react";
import { cn } from "@/lib/utils";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { MarkdownRenderer } from "./MarkdownRenderer";
import type { Message } from "@/types";

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-4 px-4 py-6",
        isUser ? "bg-background" : "bg-muted/30"
      )}
    >
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback
          className={cn(
            "text-xs",
            isUser ? "bg-primary text-primary-foreground" : "bg-secondary"
          )}
        >
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>

      <div className="min-w-0 flex-1">
        <div className="mb-1 text-sm font-medium">
          {isUser ? "You" : "Assistant"}
        </div>
        {isUser ? (
          <p className="whitespace-pre-wrap text-sm">{message.content}</p>
        ) : (
          <MarkdownRenderer content={message.content} />
        )}

        {message.workflowId && (
          <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
            <Workflow className="h-3 w-3" />
            <span>Workflow created</span>
          </div>
        )}
      </div>
    </div>
  );
}

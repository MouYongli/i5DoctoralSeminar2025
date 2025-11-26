"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  MessageSquare,
  GitBranch,
  Plus,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useChatStore } from "@/stores";
import { useState, useEffect } from "react";

const navigation = [
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Workflows", href: "/workflows", icon: GitBranch },
];

export function Sidebar() {
  const pathname = usePathname();
  const { conversations, loadConversations, isLoading } = useChatStore();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  return (
    <TooltipProvider delayDuration={0}>
      <aside
        className={cn(
          "flex h-full flex-col border-r bg-card transition-all duration-300",
          collapsed ? "w-16" : "w-64"
        )}
      >
        {/* Header */}
        <div className="flex h-14 items-center justify-between px-4">
          {!collapsed && (
            <Link href="/" className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                <span className="text-sm font-bold text-primary-foreground">
                  AI
                </span>
              </div>
              <span className="font-semibold">Assistant</span>
            </Link>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className={cn(collapsed && "mx-auto")}
          >
            {collapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronLeft className="h-4 w-4" />
            )}
          </Button>
        </div>

        <Separator />

        {/* New Chat Button */}
        <div className="p-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                asChild
                className={cn("w-full", collapsed && "px-0")}
                variant="outline"
              >
                <Link href="/chat">
                  <Plus className="h-4 w-4" />
                  {!collapsed && <span>New Chat</span>}
                </Link>
              </Button>
            </TooltipTrigger>
            {collapsed && <TooltipContent side="right">New Chat</TooltipContent>}
          </Tooltip>
        </div>

        {/* Navigation */}
        <nav className="space-y-1 px-3">
          {navigation.map((item) => {
            const isActive = pathname.startsWith(item.href);
            return (
              <Tooltip key={item.name}>
                <TooltipTrigger asChild>
                  <Link
                    href={item.href}
                    className={cn(
                      "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-accent text-accent-foreground"
                        : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                      collapsed && "justify-center px-0"
                    )}
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    {!collapsed && <span>{item.name}</span>}
                  </Link>
                </TooltipTrigger>
                {collapsed && (
                  <TooltipContent side="right">{item.name}</TooltipContent>
                )}
              </Tooltip>
            );
          })}
        </nav>

        <Separator className="my-3" />

        {/* Conversations List */}
        {!collapsed && (
          <div className="flex-1 overflow-hidden">
            <div className="px-4 py-2">
              <span className="text-xs font-medium text-muted-foreground">
                Recent Chats
              </span>
            </div>
            <ScrollArea className="h-full px-3">
              <div className="space-y-1 pb-4">
                {isLoading ? (
                  <p className="px-3 py-2 text-sm text-muted-foreground">
                    Loading...
                  </p>
                ) : conversations.length === 0 ? (
                  <p className="px-3 py-2 text-sm text-muted-foreground">
                    No conversations yet
                  </p>
                ) : (
                  conversations.map((conversation) => (
                    <Link
                      key={conversation.id}
                      href={`/chat/${conversation.id}`}
                      className={cn(
                        "block truncate rounded-md px-3 py-2 text-sm transition-colors",
                        pathname === `/chat/${conversation.id}`
                          ? "bg-accent text-accent-foreground"
                          : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                      )}
                    >
                      {conversation.title || "New Chat"}
                    </Link>
                  ))
                )}
              </div>
            </ScrollArea>
          </div>
        )}

        {/* Footer */}
        <div className="mt-auto border-t p-3">
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                variant="ghost"
                size={collapsed ? "icon" : "default"}
                className={cn("w-full", !collapsed && "justify-start")}
              >
                <Settings className="h-4 w-4" />
                {!collapsed && <span className="ml-2">Settings</span>}
              </Button>
            </TooltipTrigger>
            {collapsed && (
              <TooltipContent side="right">Settings</TooltipContent>
            )}
          </Tooltip>
        </div>
      </aside>
    </TooltipProvider>
  );
}

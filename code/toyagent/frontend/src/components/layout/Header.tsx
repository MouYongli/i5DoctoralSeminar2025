"use client";

import { usePathname } from "next/navigation";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Sun, Moon } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";

function getPageTitle(pathname: string): string {
  if (pathname === "/chat" || pathname === "/") return "Chat";
  if (pathname.startsWith("/chat/")) return "Chat";
  if (pathname === "/workflows") return "Workflows";
  if (pathname.includes("/workflows/") && pathname.includes("/edit"))
    return "Edit Workflow";
  if (pathname.startsWith("/workflows/")) return "Workflow";
  return "AI Assistant";
}

export function Header() {
  const pathname = usePathname();
  const title = getPageTitle(pathname);
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="flex h-14 items-center justify-between border-b bg-card px-6">
      <h1 className="text-lg font-semibold">{title}</h1>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={toggleTheme}>
          {theme === "dark" ? (
            <Sun className="h-4 w-4" />
          ) : (
            <Moon className="h-4 w-4" />
          )}
        </Button>

        <Avatar className="h-8 w-8">
          <AvatarFallback className="text-xs">U</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}

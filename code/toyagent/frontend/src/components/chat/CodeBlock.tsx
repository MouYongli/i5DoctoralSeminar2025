"use client";

import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface CodeBlockProps {
  code: string;
  language?: string;
  className?: string;
}

export function CodeBlock({ code, language, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn("group relative", className)}>
      <div className="flex items-center justify-between rounded-t-lg border border-b-0 bg-muted px-4 py-2">
        <span className="text-xs font-medium text-muted-foreground">
          {language || "code"}
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="h-6 w-6 opacity-0 transition-opacity group-hover:opacity-100"
          onClick={copyToClipboard}
        >
          {copied ? (
            <Check className="h-3 w-3 text-green-500" />
          ) : (
            <Copy className="h-3 w-3" />
          )}
        </Button>
      </div>
      <pre className="overflow-x-auto rounded-b-lg border bg-muted/50 p-4">
        <code className="font-mono text-sm">{code}</code>
      </pre>
    </div>
  );
}

"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { cn } from "@/lib/utils";
import { CodeBlock } from "./CodeBlock";
import type { Components } from "react-markdown";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  const components: Components = {
    code({ className: codeClassName, children, ...props }) {
      const match = /language-(\w+)/.exec(codeClassName || "");
      const isInline = !match;

      if (isInline) {
        return (
          <code
            className="rounded bg-muted px-1.5 py-0.5 font-mono text-sm"
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <CodeBlock
          code={String(children).replace(/\n$/, "")}
          language={match?.[1]}
        />
      );
    },
    pre({ children }) {
      return <>{children}</>;
    },
    a({ href, children }) {
      return (
        <a
          href={href}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-500 underline hover:text-blue-600"
        >
          {children}
        </a>
      );
    },
    ul({ children }) {
      return <ul className="my-2 ml-4 list-disc space-y-1">{children}</ul>;
    },
    ol({ children }) {
      return <ol className="my-2 ml-4 list-decimal space-y-1">{children}</ol>;
    },
    blockquote({ children }) {
      return (
        <blockquote className="my-2 border-l-2 border-muted-foreground/30 pl-4 italic text-muted-foreground">
          {children}
        </blockquote>
      );
    },
    h1({ children }) {
      return <h1 className="mb-2 mt-4 text-2xl font-bold">{children}</h1>;
    },
    h2({ children }) {
      return <h2 className="mb-2 mt-3 text-xl font-semibold">{children}</h2>;
    },
    h3({ children }) {
      return <h3 className="mb-2 mt-3 text-lg font-medium">{children}</h3>;
    },
    p({ children }) {
      return <p className="my-2 leading-7">{children}</p>;
    },
    table({ children }) {
      return (
        <div className="my-4 overflow-x-auto">
          <table className="w-full border-collapse border">{children}</table>
        </div>
      );
    },
    th({ children }) {
      return (
        <th className="border bg-muted px-4 py-2 text-left font-medium">
          {children}
        </th>
      );
    },
    td({ children }) {
      return <td className="border px-4 py-2">{children}</td>;
    },
  };

  return (
    <div className={cn("prose prose-sm dark:prose-invert max-w-none", className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeHighlight]}
        components={components}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

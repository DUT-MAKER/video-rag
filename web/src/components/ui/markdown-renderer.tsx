"use client";

import * as React from "react";
import { Check, Copy } from "lucide-react";
import { cn } from "@/lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export function MarkdownRenderer({
  content,
  className,
}: MarkdownRendererProps) {
  const blocks = React.useMemo(() => parseMarkdownBlocks(content), [content]);

  return (
    <div
      className={cn(
        "text-foreground space-y-3 text-[15px] leading-relaxed",
        className
      )}
    >
      {blocks.map((block, idx) => (
        <React.Fragment key={idx}>{renderBlock(block, idx)}</React.Fragment>
      ))}
    </div>
  );
}

// ---------------------- BLOCK PARSER ----------------------

type Block =
  | { type: "heading"; level: number; text: string }
  | { type: "paragraph"; text: string }
  | { type: "code"; language: string; code: string }
  | { type: "blockquote"; text: string }
  | { type: "ul"; items: string[] }
  | { type: "ol"; items: string[] }
  | { type: "hr" };

function parseMarkdownBlocks(raw: string): Block[] {
  const lines = raw.split("\n");
  const blocks: Block[] = [];

  let inCodeBlock = false;
  let codeLang = "";
  let codeLines: string[] = [];

  let currentList: { type: "ul" | "ol"; items: string[] } | null = null;

  const flushList = () => {
    if (currentList) {
      blocks.push(currentList);
      currentList = null;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Code block fences: ```lang
    if (line.trim().startsWith("```")) {
      flushList();
      if (inCodeBlock) {
        blocks.push({
          type: "code",
          language: codeLang,
          code: codeLines.join("\n"),
        });
        inCodeBlock = false;
        codeLines = [];
        codeLang = "";
      } else {
        inCodeBlock = true;
        codeLang = line.trim().slice(3).trim();
        codeLines = [];
      }
      continue;
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    const trimmed = line.trim();

    // Empty line
    if (!trimmed) {
      flushList();
      continue;
    }

    // Horizontal Rule: --- or ***
    if (/^(\*\*\*|---|___)$/.test(trimmed)) {
      flushList();
      blocks.push({ type: "hr" });
      continue;
    }

    // Headings: #, ##, ###, ####
    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      flushList();
      blocks.push({
        type: "heading",
        level: headingMatch[1].length,
        text: headingMatch[2],
      });
      continue;
    }

    // Blockquote: > text
    if (trimmed.startsWith(">")) {
      flushList();
      const quoteText = trimmed.replace(/^>\s?/, "");
      blocks.push({
        type: "blockquote",
        text: quoteText,
      });
      continue;
    }

    // Unordered list: - item or * item
    const ulMatch = trimmed.match(/^[-*•]\s+(.+)$/);
    if (ulMatch) {
      if (!currentList || currentList.type !== "ul") {
        flushList();
        currentList = { type: "ul", items: [] };
      }
      currentList.items.push(ulMatch[1]);
      continue;
    }

    // Ordered list: 1. item
    const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
    if (olMatch) {
      if (!currentList || currentList.type !== "ol") {
        flushList();
        currentList = { type: "ol", items: [] };
      }
      currentList.items.push(olMatch[1]);
      continue;
    }

    // Default: Regular Paragraph
    flushList();
    blocks.push({
      type: "paragraph",
      text: trimmed,
    });
  }

  flushList();

  if (inCodeBlock) {
    blocks.push({
      type: "code",
      language: codeLang,
      code: codeLines.join("\n"),
    });
  }

  return blocks;
}

// ---------------------- BLOCK RENDERER ----------------------

function renderBlock(block: Block, key: number) {
  switch (block.type) {
    case "heading": {
      if (block.level === 1) {
        return (
          <h2 className="text-foreground border-border mb-1 mt-3 border-b pb-1.5 text-lg font-semibold tracking-tight">
            <InlineText text={block.text} />
          </h2>
        );
      }
      if (block.level === 2) {
        return (
          <h3 className="text-foreground mb-1 mt-2.5 text-base font-semibold tracking-tight">
            <InlineText text={block.text} />
          </h3>
        );
      }
      return (
        <h4 className="text-muted-foreground mb-0.5 mt-2 text-sm font-semibold uppercase tracking-wider">
          <InlineText text={block.text} />
        </h4>
      );
    }

    case "paragraph":
      return (
        <p className="leading-relaxed">
          <InlineText text={block.text} />
        </p>
      );

    case "blockquote":
      return (
        <blockquote className="border-accent bg-accent/10 text-foreground my-2 rounded-r border-l-2 py-1.5 pl-3.5 font-medium italic leading-relaxed">
          <InlineText text={block.text} />
        </blockquote>
      );

    case "ul":
      return (
        <ul className="text-foreground my-1.5 list-inside list-disc space-y-1 pl-1">
          {block.items.map((item, i) => (
            <li key={i} className="leading-relaxed">
              <InlineText text={item} />
            </li>
          ))}
        </ul>
      );

    case "ol":
      return (
        <ol className="text-foreground my-1.5 list-inside list-decimal space-y-1 pl-1">
          {block.items.map((item, i) => (
            <li key={i} className="leading-relaxed">
              <InlineText text={item} />
            </li>
          ))}
        </ol>
      );

    case "hr":
      return <hr className="border-border my-3" />;

    case "code":
      return (
        <CodeBlock key={key} language={block.language} code={block.code} />
      );
  }
}

// ---------------------- CODE BLOCK COMPONENT ----------------------

function CodeBlock({ language, code }: { language: string; code: string }) {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="border-border bg-background my-2.5 overflow-hidden rounded-lg border">
      <div className="bg-surface border-border text-muted-foreground flex select-none items-center justify-between border-b px-3 py-1.5 font-mono text-[11px]">
        <span>{language || "code"}</span>
        <button
          type="button"
          onClick={handleCopy}
          className="hover:text-foreground flex cursor-pointer items-center gap-1 transition-colors"
        >
          {copied ? (
            <>
              <Check className="text-accent h-3 w-3" />
              <span className="text-accent font-semibold">Đã sao chép</span>
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              <span>Sao chép</span>
            </>
          )}
        </button>
      </div>
      <pre className="text-foreground overflow-x-auto p-3 font-mono text-sm leading-relaxed">
        <code>{code}</code>
      </pre>
    </div>
  );
}

// ---------------------- INLINE TEXT PARSER ----------------------
// Parses **bold**, *italic*, and `inline code`

function InlineText({ text }: { text: string }) {
  // Regex splitting by bold (**...**), inline code (`...`), and italic (*...*)
  const parts = React.useMemo(() => {
    const tokens: React.ReactNode[] = [];
    const regex = /(\*\*[^*]+\*\*|`[^`]+`|\*[^*]+\*)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      if (match.index > lastIndex) {
        tokens.push(text.substring(lastIndex, match.index));
      }

      const matchText = match[0];
      if (matchText.startsWith("**") && matchText.endsWith("**")) {
        tokens.push(
          <strong key={match.index} className="text-foreground font-semibold">
            {matchText.slice(2, -2)}
          </strong>
        );
      } else if (matchText.startsWith("`") && matchText.endsWith("`")) {
        tokens.push(
          <code
            key={match.index}
            className="bg-surface border-border text-accent rounded border px-1.5 py-0.5 font-mono text-sm font-medium"
          >
            {matchText.slice(1, -1)}
          </code>
        );
      } else if (matchText.startsWith("*") && matchText.endsWith("*")) {
        tokens.push(
          <em key={match.index} className="text-foreground italic">
            {matchText.slice(1, -1)}
          </em>
        );
      }

      lastIndex = match.index + matchText.length;
    }

    if (lastIndex < text.length) {
      tokens.push(text.substring(lastIndex));
    }

    return tokens;
  }, [text]);

  return <>{parts}</>;
}

import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "w-full rounded-lg border border-neutral-800 bg-[#121215] p-3 text-xs text-neutral-100 outline-none transition-all placeholder:text-neutral-500 focus:border-neutral-600 focus:ring-1 focus:ring-neutral-600 disabled:opacity-50 resize-none leading-relaxed",
      className
    )}
    {...props}
  />
));

Textarea.displayName = "Textarea";

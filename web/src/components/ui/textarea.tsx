import * as React from "react";
import { cn } from "@/lib/utils";

export const Textarea = React.forwardRef<
  HTMLTextAreaElement,
  React.TextareaHTMLAttributes<HTMLTextAreaElement>
>(({ className, ...props }, ref) => (
  <textarea
    ref={ref}
    className={cn(
      "w-full resize-none rounded-lg border border-[#2e3352] bg-[#161826] p-3 text-xs leading-relaxed text-[#e9e9ed] outline-none transition-all placeholder:text-[#9396aa] focus:border-[#9184d9] focus:ring-1 focus:ring-[#9184d9] disabled:opacity-40",
      className
    )}
    {...props}
  />
));

Textarea.displayName = "Textarea";

import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "h-9 w-full rounded-lg border border-neutral-800 bg-[#121215] px-3 text-xs text-neutral-100 outline-none transition-all placeholder:text-neutral-500 focus:border-neutral-600 focus:ring-1 focus:ring-neutral-600 disabled:opacity-50",
      className
    )}
    {...props}
  />
));

Input.displayName = "Input";

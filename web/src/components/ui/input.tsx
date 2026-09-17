import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "w-full rounded-xl border border-[#e2e8f0] bg-[#f8fafc] px-4 py-2.5 text-xs font-medium text-[#0f172a] outline-none transition-all placeholder:text-[#94a3b8] focus:border-[#ff7442] focus:bg-white focus:ring-4 focus:ring-[#ff7442]/10 disabled:opacity-40",
      className
    )}
    {...props}
  />
));

Input.displayName = "Input";


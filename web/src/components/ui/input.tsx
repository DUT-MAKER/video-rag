import * as React from "react";
import { cn } from "@/lib/utils";

export const Input = React.forwardRef<
  HTMLInputElement,
  React.InputHTMLAttributes<HTMLInputElement>
>(({ className, ...props }, ref) => (
  <input
    ref={ref}
    className={cn(
      "h-9 w-full rounded-lg border border-[#2e3352] bg-[#161826] px-3 text-xs text-[#e9e9ed] outline-none transition-all placeholder:text-[#9396aa] focus:border-[#9184d9] focus:ring-1 focus:ring-[#9184d9] disabled:opacity-40",
      className
    )}
    {...props}
  />
));

Input.displayName = "Input";

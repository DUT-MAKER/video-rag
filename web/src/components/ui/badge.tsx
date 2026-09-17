import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full px-3 py-1 text-xs font-bold transition-colors border select-none",
  {
    variants: {
      variant: {
        default: "border-[#ffe0d5] bg-[#fff0eb] text-[#ff7442]",
        secondary: "border-[#f1f5f9] bg-[#f8fafc] text-[#667085]",
        outline: "border-[#e2e8f0] text-[#475569] bg-white",
        accent:
          "border-[#ffe0d5] bg-[#fff0eb] text-[#ff7442] font-black",
        ai: "border-[#ffe0d5] bg-[linear-gradient(90deg,#fff0eb,#ffe4d9)] text-[#ff7442] font-black",
        hook: "border-[#ffd866] bg-[#fef9c3] text-[#d97706] font-black tracking-wide",
        success:
          "border-emerald-100 bg-emerald-50 text-emerald-700 font-extrabold",
        mono: "font-mono text-[11px] tracking-wider uppercase border-[#e2e8f0] bg-[#f8fafc] text-[#475569] font-bold",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends
    React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}


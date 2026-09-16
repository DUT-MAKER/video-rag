import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium transition-colors border select-none",
  {
    variants: {
      variant: {
        default: "border-[#2e3352] bg-[#1d2035] text-[#e9e9ed]",
        secondary: "border-[#23273e] bg-[#161826] text-[#9396aa]",
        outline: "border-[#2e3352] text-[#e9e9ed] bg-transparent",
        accent:
          "border-[#9184d9]/50 bg-[#9184d9]/15 text-[#c5bdf0] font-semibold",
        ai: "border-[#9184d9]/50 bg-[#9184d9]/15 text-[#c5bdf0] font-semibold",
        hook: "border-orange-400/40 bg-orange-500/10 text-orange-200 font-semibold tracking-wide",
        success:
          "border-emerald-400/40 bg-emerald-500/10 text-emerald-200 font-semibold",
        mono: "font-mono text-[10px] tracking-wider uppercase border-[#2e3352] bg-[#1d2035] text-[#e9e9ed]",
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

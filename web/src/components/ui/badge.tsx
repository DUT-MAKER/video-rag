import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium transition-colors border select-none",
  {
    variants: {
      variant: {
        default:
          "border-neutral-800 bg-neutral-900 text-neutral-300",
        secondary:
          "border-neutral-800/60 bg-neutral-800/40 text-neutral-400",
        outline:
          "border-neutral-700/60 text-neutral-300 bg-transparent",
        hook:
          "border-orange-500/20 bg-orange-500/10 text-orange-400 font-semibold tracking-wide",
        ai:
          "border-purple-500/20 bg-purple-500/10 text-purple-300 font-medium",
        success:
          "border-emerald-500/20 bg-emerald-500/10 text-emerald-400 font-medium",
        mono:
          "font-mono text-[10px] tracking-wider uppercase border-neutral-800 bg-black/40 text-neutral-400",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#9184d9] focus-visible:ring-offset-2 focus-visible:ring-offset-[#161826] disabled:pointer-events-none disabled:opacity-40 select-none cursor-pointer active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "border border-[#9184d9] text-[#e9e9ed] bg-[#9184d9]/10 hover:bg-[#9184d9]/20 hover:border-[#a89de3] hover:shadow-[0_0_12px_rgba(145,132,217,0.25)] font-semibold",
        solid:
          "bg-[#9184d9] text-[#161826] hover:bg-[#a89de3] font-bold shadow-xs",
        secondary:
          "bg-[#1d2035] border border-[#2e3352] text-[#e9e9ed] hover:bg-[#262a45] hover:border-[#3d446c]",
        outline:
          "border border-[#2e3352] text-[#e9e9ed] bg-transparent hover:bg-[#1d2035] hover:border-[#3d446c]",
        ghost: "text-[#9396aa] hover:text-[#e9e9ed] hover:bg-[#1d2035]",
        hook: "bg-orange-500/10 border border-orange-400/30 text-orange-300 hover:bg-orange-500/20 hover:border-orange-400/50 font-semibold",
        destructive:
          "bg-red-500/10 border border-red-500/30 text-red-300 hover:bg-red-500/20",
      },
      size: {
        sm: "h-8 px-3 gap-1.5",
        md: "h-9 px-3.5 gap-2",
        lg: "h-11 px-6 gap-2 text-sm",
        icon: "h-8 w-8",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";

    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

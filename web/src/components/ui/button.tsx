import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-lg text-xs font-medium transition-all focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-neutral-400 disabled:pointer-events-none disabled:opacity-40 select-none cursor-pointer active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-white text-neutral-950 hover:bg-neutral-200 shadow-sm font-semibold",
        secondary:
          "bg-neutral-900 border border-neutral-800 text-neutral-200 hover:bg-neutral-800/80 hover:text-white hover:border-neutral-700",
        outline:
          "border border-neutral-800 bg-transparent text-neutral-300 hover:bg-neutral-900 hover:text-white",
        ghost:
          "text-neutral-400 hover:text-neutral-100 hover:bg-neutral-800/60",
        hook:
          "bg-orange-500/10 border border-orange-500/25 text-orange-400 hover:bg-orange-500/20 hover:border-orange-500/40",
        destructive:
          "bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20",
      },
      size: {
        sm: "h-8 px-2.5 gap-1.5",
        md: "h-9 px-3.5 gap-2",
        lg: "h-10 px-4 gap-2 text-sm",
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
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
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

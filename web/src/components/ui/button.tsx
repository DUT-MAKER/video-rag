import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import * as React from "react";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-full text-xs font-bold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#ff7442] focus-visible:ring-offset-2 focus-visible:ring-offset-white disabled:pointer-events-none disabled:opacity-40 select-none cursor-pointer active:scale-[0.98]",
  {
    variants: {
      variant: {
        primary:
          "bg-[linear-gradient(90deg,#ff7442,#ff8c64)] text-white shadow-[0_10px_25px_rgba(255,116,66,0.22)] hover:-translate-y-0.5 hover:shadow-[0_12px_28px_rgba(255,116,66,0.3)] font-extrabold",
        solid:
          "bg-[#ff7442] text-white hover:bg-[#e6521e] font-bold shadow-xs",
        secondary:
          "border border-[#ffe6dc] bg-white text-[#475569] shadow-[0_4px_12px_rgba(0,0,0,0.03)] hover:bg-[#fff7f4] hover:text-[#0f172a] hover:border-[#ffd0bf]",
        soft:
          "border border-[#ffe0d5] bg-[#fff0eb] text-[#ff7442] hover:bg-[#ffe4d9] font-bold",
        outline:
          "border border-[#e2e8f0] text-[#0f172a] bg-white hover:bg-[#fffbf9] hover:border-[#ff7442]/50",
        ghost: "text-[#667085] hover:text-[#0f172a] hover:bg-[#fff0eb]",
        hook: "bg-[#fff0eb] border border-[#ffe0d5] text-[#ff7442] hover:bg-[#ffe4d9] font-bold",
        dark: "bg-[#0f172a] text-white hover:bg-[#1e293b] font-bold shadow-sm",
        destructive:
          "bg-red-50 border border-red-200 text-red-600 hover:bg-red-100",
      },
      size: {
        sm: "h-8 px-3.5 gap-1.5 text-xs",
        md: "h-10 px-4.5 gap-2 text-xs",
        lg: "h-12 px-6 gap-2.5 text-sm",
        icon: "h-9 w-9",
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


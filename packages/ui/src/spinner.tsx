import { createElement } from "react";

export interface SpinnerProps {
  /** Accessible label announced by screen readers while content loads. */
  label?: string;
  className?: string;
}

/** Loading indicator; animation styles land with the Phase 10 design system. */
export function Spinner({ label = "Loading", className }: SpinnerProps) {
  return createElement("span", {
    className,
    role: "progressbar",
    "aria-label": label,
    "aria-busy": true,
  });
}

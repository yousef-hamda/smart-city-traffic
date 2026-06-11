import { createElement, type ReactNode } from "react";

export interface BadgeProps {
  children: ReactNode;
  /** Semantic tone; concrete Tailwind variants land with the Phase 10 design system. */
  tone?: "neutral" | "success" | "warning" | "danger";
  className?: string;
}

/** Small status label used for severity / health indicators across apps. */
export function Badge({ children, tone = "neutral", className }: BadgeProps) {
  return createElement("span", { className, "data-tone": tone, role: "status" }, children);
}

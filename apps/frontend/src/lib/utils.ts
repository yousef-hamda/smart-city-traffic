import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getStatusColor(status: string): string {
  switch (status) {
    case "green":
      return "#22c55e";
    case "amber":
      return "#f59e0b";
    case "red":
      return "#ef4444";
    default:
      return "#64748b";
  }
}

export function getStatusBgClass(status: string): string {
  switch (status) {
    case "green":
      return "bg-green-500/20 text-green-400 border-green-500/30";
    case "amber":
      return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    case "red":
      return "bg-red-500/20 text-red-400 border-red-500/30";
    default:
      return "bg-slate-700/50 text-slate-400 border-slate-600/30";
  }
}

export function formatSpeed(speed: number): string {
  return `${speed} km/h`;
}

export function formatTimestamp(ts: number): string {
  return new Intl.DateTimeFormat("en", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(ts));
}

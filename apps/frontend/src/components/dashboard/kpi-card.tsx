import * as React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: "up" | "down" | "neutral";
  icon: string;
  loading?: boolean;
  colorClass?: string;
}

export function KPICard({
  title,
  value,
  unit,
  trend,
  icon,
  loading,
  colorClass = "text-indigo-400",
}: KPICardProps) {
  if (loading) {
    return (
      <Card>
        <CardContent className="p-5">
          <Skeleton className="h-4 w-24 mb-3" />
          <Skeleton className="h-8 w-16" />
        </CardContent>
      </Card>
    );
  }
  return (
    <Card className="hover:border-indigo-500/40 transition-colors">
      <CardContent className="p-5">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-slate-400 mb-1">{title}</p>
            <div className="flex items-baseline gap-1">
              <span className={`text-2xl font-bold ${colorClass}`}>{value}</span>
              {unit && <span className="text-sm text-slate-500">{unit}</span>}
            </div>
          </div>
          <div className="text-2xl opacity-80">{icon}</div>
        </div>
        {trend && (
          <div className="mt-2 text-xs text-slate-500">
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} vs last hour
          </div>
        )}
      </CardContent>
    </Card>
  );
}

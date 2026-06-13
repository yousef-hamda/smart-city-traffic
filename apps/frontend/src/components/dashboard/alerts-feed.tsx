"use client";

import * as React from "react";
import { useTrafficStore } from "@/store/traffic";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatTimestamp } from "@/lib/utils";
import type { Alert } from "@/lib/types";

const SEVERITY_VARIANT: Record<
  Alert["severity"],
  "destructive" | "warning" | "secondary" | "outline"
> = {
  critical: "destructive",
  high: "destructive",
  medium: "warning",
  low: "secondary",
};

export function AlertsFeed() {
  const alerts = useTrafficStore((s) => s.alerts);
  const acknowledgeAlert = useTrafficStore((s) => s.acknowledgeAlert);

  if (alerts.length === 0) {
    return (
      <div className="text-center text-slate-500 py-8">
        <p className="text-lg">No active alerts</p>
        <p className="text-sm mt-1">All clear</p>
      </div>
    );
  }

  return (
    <div className="space-y-2 max-h-80 overflow-y-auto">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className={`flex items-start gap-3 p-3 rounded-lg border transition-opacity ${
            alert.acknowledged
              ? "opacity-50 border-slate-700/30"
              : "border-slate-700/50 bg-slate-800/30"
          }`}
        >
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <Badge variant={SEVERITY_VARIANT[alert.severity]}>{alert.severity}</Badge>
              <span className="text-xs text-slate-500">{alert.type}</span>
              <span className="text-xs text-slate-600">{formatTimestamp(alert.timestamp)}</span>
            </div>
            <p className="text-sm text-slate-300 truncate">{alert.message}</p>
            <p className="text-xs text-slate-500">{alert.segment_name}</p>
          </div>
          {!alert.acknowledged && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => acknowledgeAlert(alert.id)}
              className="text-xs shrink-0"
            >
              Ack
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}

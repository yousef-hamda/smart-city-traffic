"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { useTrafficStore } from "@/store/traffic";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { getStatusBgClass } from "@/lib/utils";

const TwinScene = dynamic(
  () => import("@/components/twin/twin-scene").then((m) => ({ default: m.TwinScene })),
  {
    ssr: false,
    loading: () => (
      <div className="flex items-center justify-center h-full text-slate-500">
        <div className="text-center space-y-2">
          <Skeleton className="w-16 h-16 rounded-full mx-auto" />
          <p className="text-sm">Loading 3D scene...</p>
        </div>
      </div>
    ),
  },
);

export default function TwinPage() {
  const segments = useTrafficStore((s) => Object.values(s.segments));
  const usingMock = useTrafficStore((s) => s.usingMockData);
  const [selectedId, setSelectedId] = React.useState<string | undefined>();

  const selectedSegment = selectedId ? segments.find((s) => s.id === selectedId) : null;

  return (
    <div className="flex flex-col h-full p-4 gap-4">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 className="text-xl font-bold text-slate-100">3D Digital Twin</h1>
          <p className="text-sm text-slate-400">Jerusalem Road Network — Interactive View</p>
        </div>
        <div className="flex items-center gap-2">
          {usingMock && (
            <Badge variant="warning" className="animate-pulse text-xs">
              Demo Data
            </Badge>
          )}
          <Badge variant="secondary" className="text-xs">
            {segments.length} segments
          </Badge>
        </div>
      </div>

      {/* Main view */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-4 gap-4 min-h-0">
        {/* 3D canvas */}
        <div className="lg:col-span-3 rounded-xl overflow-hidden border border-slate-700/50 bg-slate-950">
          <div style={{ height: "500px" }}>
            <TwinScene
              segments={segments}
              selectedId={selectedId}
              onSelectSegment={setSelectedId}
            />
          </div>
        </div>

        {/* Segment info panel */}
        <div className="space-y-3">
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-slate-500 mb-3 font-medium uppercase tracking-wide">
                Selected Segment
              </p>
              {selectedSegment ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-slate-200">{selectedSegment.name_en}</p>
                  <Badge className={getStatusBgClass(selectedSegment.status)}>
                    {selectedSegment.status}
                  </Badge>
                  <div className="grid grid-cols-2 gap-2 mt-2 text-xs text-slate-400">
                    <div>
                      <span className="block text-slate-500">Live speed</span>
                      <span className="text-slate-200 font-medium">
                        {selectedSegment.live_speed} km/h
                      </span>
                    </div>
                    <div>
                      <span className="block text-slate-500">Limit</span>
                      <span className="text-slate-200 font-medium">
                        {selectedSegment.speed_limit} km/h
                      </span>
                    </div>
                  </div>
                </div>
              ) : (
                <p className="text-xs text-slate-500">Click a road segment in the 3D view</p>
              )}
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-slate-500 mb-3 font-medium uppercase tracking-wide">
                Status Legend
              </p>
              <div className="space-y-2">
                {[
                  { status: "green", label: "Free flow" },
                  { status: "amber", label: "Moderate" },
                  { status: "red", label: "Congested" },
                ].map(({ status, label }) => (
                  <div key={status} className="flex items-center gap-2">
                    <div
                      className="w-3 h-3 rounded-sm"
                      style={{
                        backgroundColor:
                          status === "green"
                            ? "#22c55e"
                            : status === "amber"
                              ? "#f59e0b"
                              : "#ef4444",
                      }}
                    />
                    <span className="text-xs text-slate-400">{label}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Controls hint */}
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-slate-500 mb-2 font-medium uppercase tracking-wide">
                Controls
              </p>
              <ul className="text-xs text-slate-500 space-y-1">
                <li>Left drag — orbit</li>
                <li>Right drag — pan</li>
                <li>Scroll — zoom</li>
                <li>Click segment — select</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

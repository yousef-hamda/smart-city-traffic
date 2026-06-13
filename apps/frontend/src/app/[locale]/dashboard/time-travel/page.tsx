"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { useTrafficStore } from "@/store/traffic";
import { getHistoryBuffer } from "@/lib/mock";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const TrafficMap = dynamic(
  () => import("@/components/dashboard/traffic-map").then((m) => ({ default: m.TrafficMap })),
  {
    ssr: false,
    loading: () => <Skeleton className="w-full h-96 rounded-lg" />,
  },
);

const OFFSET_STEPS = [0, 15, 30, 60, 120, 180, 240, 360, 480] as const;

export default function TimeTravelPage() {
  const liveSegments = useTrafficStore((s) => Object.values(s.segments));
  const [offsetMinutes, setOffsetMinutes] = React.useState(0);
  const [isPlaying, setIsPlaying] = React.useState(false);
  const playIntervalRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  const displaySegments = React.useMemo(() => {
    if (offsetMinutes === 0) return liveSegments;
    return getHistoryBuffer(offsetMinutes);
  }, [offsetMinutes, liveSegments]);

  const statusSummary = React.useMemo(() => {
    const counts = { green: 0, amber: 0, red: 0 };
    displaySegments.forEach((s) => {
      if (s.status in counts) counts[s.status as keyof typeof counts]++;
    });
    return counts;
  }, [displaySegments]);

  function togglePlay() {
    if (isPlaying) {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
      setIsPlaying(false);
      return;
    }
    setIsPlaying(true);
    let stepIndex = OFFSET_STEPS.indexOf(offsetMinutes as (typeof OFFSET_STEPS)[number]);
    if (stepIndex < 0) stepIndex = 0;
    playIntervalRef.current = setInterval(() => {
      stepIndex = (stepIndex + 1) % OFFSET_STEPS.length;
      setOffsetMinutes(OFFSET_STEPS[stepIndex]);
    }, 1500);
  }

  React.useEffect(() => {
    return () => {
      if (playIntervalRef.current) clearInterval(playIntervalRef.current);
    };
  }, []);

  const nowLabel = offsetMinutes === 0 ? "Live" : `−${offsetMinutes}m ago`;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Time Travel</h1>
          <p className="text-sm text-slate-400 mt-1">
            Replay historical traffic states across the road network
          </p>
        </div>
        <Badge variant={offsetMinutes === 0 ? "success" : "secondary"} className="text-sm px-3">
          {nowLabel}
        </Badge>
      </div>

      {/* Timeline controls */}
      <Card>
        <CardContent className="p-5 space-y-4">
          <div className="flex items-center gap-4 flex-wrap">
            <span className="text-sm text-slate-400 font-medium">Timeline:</span>
            <div className="flex flex-wrap gap-2">
              {OFFSET_STEPS.map((step) => (
                <button
                  key={step}
                  onClick={() => setOffsetMinutes(step)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-colors ${
                    offsetMinutes === step
                      ? "bg-indigo-600 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-100"
                  }`}
                >
                  {step === 0 ? "Now" : `-${step}m`}
                </button>
              ))}
            </div>
          </div>

          {/* Slider */}
          <div className="flex items-center gap-4">
            <span className="text-xs text-slate-500 w-12">-8h</span>
            <input
              type="range"
              min={0}
              max={480}
              step={15}
              value={offsetMinutes}
              onChange={(e) => setOffsetMinutes(Number(e.target.value))}
              className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <span className="text-xs text-slate-500 w-12">Now</span>
          </div>

          <div className="flex items-center gap-3">
            <Button size="sm" variant={isPlaying ? "secondary" : "default"} onClick={togglePlay}>
              {isPlaying ? "⏸ Pause" : "▶ Play"}
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => {
                setOffsetMinutes(0);
                if (isPlaying) {
                  if (playIntervalRef.current) clearInterval(playIntervalRef.current);
                  setIsPlaying(false);
                }
              }}
            >
              ⏮ Reset to Live
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Status summary */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Free flow", key: "green", color: "text-green-400" },
          { label: "Moderate", key: "amber", color: "text-amber-400" },
          { label: "Congested", key: "red", color: "text-red-400" },
        ].map(({ label, key, color }) => (
          <Card key={key}>
            <CardContent className="p-4 text-center">
              <p className={`text-2xl font-bold ${color}`}>
                {statusSummary[key as keyof typeof statusSummary]}
              </p>
              <p className="text-xs text-slate-500 mt-1">{label}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Map */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Traffic Map at {nowLabel}</CardTitle>
        </CardHeader>
        <CardContent className="p-0 px-4 pb-4">
          <div style={{ height: "450px" }}>
            <TrafficMap segments={displaySegments} />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

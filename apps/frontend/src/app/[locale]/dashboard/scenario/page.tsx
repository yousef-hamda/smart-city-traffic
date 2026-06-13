"use client";

import * as React from "react";
import { useTrafficStore } from "@/store/traffic";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getStatusBgClass } from "@/lib/utils";
import type { ScenarioResult, SegmentStatus } from "@/lib/types";

interface ScenarioConfig {
  name: string;
  description: string;
  speedFactor: number;
}

const SCENARIOS: ScenarioConfig[] = [
  {
    name: "Peak Hour",
    description: "Simulate morning rush hour — all segments at 50% capacity",
    speedFactor: 0.5,
  },
  {
    name: "Road Closure",
    description: "Close two major arteries and re-route traffic",
    speedFactor: 0.3,
  },
  {
    name: "Special Event",
    description: "Large event at city center generating 30% more vehicles",
    speedFactor: 0.65,
  },
  {
    name: "Optimal Flow",
    description: "AI-optimised signal timing achieving near-free-flow",
    speedFactor: 0.9,
  },
];

function computeStatus(speed: number, limit: number): SegmentStatus {
  const ratio = speed / limit;
  if (ratio >= 0.7) return "green";
  if (ratio >= 0.4) return "amber";
  return "red";
}

export default function ScenarioPage() {
  const segments = useTrafficStore((s) => Object.values(s.segments));
  const [selectedScenario, setSelectedScenario] = React.useState<ScenarioConfig | null>(null);
  const [results, setResults] = React.useState<ScenarioResult[]>([]);
  const [running, setRunning] = React.useState(false);

  async function runScenario(scenario: ScenarioConfig) {
    setSelectedScenario(scenario);
    setRunning(true);
    // Simulate processing delay
    await new Promise<void>((resolve) => setTimeout(resolve, 800));
    const scenarioResults: ScenarioResult[] = segments.map((seg) => {
      const newSpeed = Math.max(5, Math.round(seg.live_speed * scenario.speedFactor));
      const newStatus = computeStatus(newSpeed, seg.speed_limit);
      return {
        segment_id: seg.id,
        predicted_speed_change: newSpeed - seg.live_speed,
        predicted_status: newStatus,
        impact_magnitude: Math.abs(newSpeed - seg.live_speed),
      };
    });
    setResults(scenarioResults);
    setRunning(false);
  }

  const impactSummary = React.useMemo(() => {
    if (!results.length) return null;
    const improved = results.filter((r) => r.predicted_speed_change > 0).length;
    const worsened = results.filter((r) => r.predicted_speed_change < 0).length;
    const avgChange =
      results.reduce((sum, r) => sum + r.predicted_speed_change, 0) / results.length;
    return { improved, worsened, avgChange: Math.round(avgChange * 10) / 10 };
  }, [results]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Scenario Simulator</h1>
        <p className="text-sm text-slate-400 mt-1">
          Simulate traffic scenarios and predict network impact
        </p>
      </div>

      {/* Scenario cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {SCENARIOS.map((scenario) => (
          <Card
            key={scenario.name}
            className={`cursor-pointer transition-all hover:border-indigo-500/50 ${
              selectedScenario?.name === scenario.name
                ? "border-indigo-500/70 bg-indigo-950/20"
                : ""
            }`}
          >
            <CardContent className="p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className="font-semibold text-slate-100 mb-1">{scenario.name}</h3>
                  <p className="text-sm text-slate-400">{scenario.description}</p>
                  <div className="mt-2">
                    <Badge variant="secondary" className="text-xs">
                      Speed factor: {Math.round(scenario.speedFactor * 100)}%
                    </Badge>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant={selectedScenario?.name === scenario.name ? "default" : "outline"}
                  onClick={() => runScenario(scenario)}
                  disabled={running}
                >
                  {running && selectedScenario?.name === scenario.name ? "Running..." : "Run"}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Results */}
      {results.length > 0 && selectedScenario && (
        <>
          {/* Impact summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Impact Summary — {selectedScenario.name}</CardTitle>
            </CardHeader>
            <CardContent>
              {impactSummary && (
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-green-400">{impactSummary.improved}</p>
                    <p className="text-xs text-slate-500">Segments improved</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-red-400">{impactSummary.worsened}</p>
                    <p className="text-xs text-slate-500">Segments worsened</p>
                  </div>
                  <div>
                    <p
                      className={`text-2xl font-bold ${impactSummary.avgChange >= 0 ? "text-green-400" : "text-red-400"}`}
                    >
                      {impactSummary.avgChange > 0 ? "+" : ""}
                      {impactSummary.avgChange} km/h
                    </p>
                    <p className="text-xs text-slate-500">Avg speed change</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Segment results table */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Segment-Level Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto max-h-80">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left border-b border-slate-700">
                      <th className="pb-2 text-slate-400 font-medium">Segment ID</th>
                      <th className="pb-2 text-slate-400 font-medium">Speed Change</th>
                      <th className="pb-2 text-slate-400 font-medium">Predicted Status</th>
                      <th className="pb-2 text-slate-400 font-medium">Impact</th>
                    </tr>
                  </thead>
                  <tbody>
                    {results.slice(0, 20).map((r) => (
                      <tr key={r.segment_id} className="border-b border-slate-800">
                        <td className="py-1.5 text-slate-400 text-xs">{r.segment_id}</td>
                        <td
                          className={`py-1.5 font-medium ${r.predicted_speed_change >= 0 ? "text-green-400" : "text-red-400"}`}
                        >
                          {r.predicted_speed_change > 0 ? "+" : ""}
                          {r.predicted_speed_change} km/h
                        </td>
                        <td className="py-1.5">
                          <Badge className={getStatusBgClass(r.predicted_status)}>
                            {r.predicted_status}
                          </Badge>
                        </td>
                        <td className="py-1.5 text-slate-500 text-xs">{r.impact_magnitude} km/h</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {results.length > 20 && (
                  <p className="text-xs text-slate-500 mt-2 text-center">
                    Showing 20 of {results.length} segments
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}

"use client";

import * as React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { useTrafficStore } from "@/store/traffic";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

const STATUS_COLORS = {
  green: "#22c55e",
  amber: "#f59e0b",
  red: "#ef4444",
  unknown: "#64748b",
};

export default function AnalyticsPage() {
  const segments = useTrafficStore((s) => Object.values(s.segments));

  // Compute distribution by status
  const statusDistribution = React.useMemo(() => {
    const counts: Record<string, number> = { green: 0, amber: 0, red: 0, unknown: 0 };
    segments.forEach((s) => {
      counts[s.status] = (counts[s.status] ?? 0) + 1;
    });
    return Object.entries(counts).map(([name, value]) => ({ name, value }));
  }, [segments]);

  // Top congested segments
  const topCongested = React.useMemo(
    () =>
      [...segments]
        .sort((a, b) => a.live_speed / a.speed_limit - b.live_speed / b.speed_limit)
        .slice(0, 10)
        .map((s) => ({
          name: s.road.replace(/-/g, " ").slice(0, 16),
          speed: s.live_speed,
          limit: s.speed_limit,
          ratio: Math.round((s.live_speed / s.speed_limit) * 100),
        })),
    [segments],
  );

  // Speed distribution histogram
  const speedHistogram = React.useMemo(() => {
    const buckets: Record<string, number> = {
      "0–20": 0,
      "20–40": 0,
      "40–60": 0,
      "60–80": 0,
      "80+": 0,
    };
    segments.forEach((s) => {
      if (s.live_speed < 20) buckets["0–20"]++;
      else if (s.live_speed < 40) buckets["20–40"]++;
      else if (s.live_speed < 60) buckets["40–60"]++;
      else if (s.live_speed < 80) buckets["60–80"]++;
      else buckets["80+"]++;
    });
    return Object.entries(buckets).map(([range, count]) => ({ range, count }));
  }, [segments]);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-100">Analytics</h1>
        <p className="text-sm text-slate-400 mt-1">Network-wide traffic statistics</p>
      </div>

      {/* Summary row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {statusDistribution.map(({ name, value }) => (
          <Card key={name}>
            <CardContent className="p-4 flex items-center gap-3">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: STATUS_COLORS[name as keyof typeof STATUS_COLORS] }}
              />
              <div>
                <p className="text-xs text-slate-500 capitalize">{name}</p>
                <p className="text-lg font-bold text-slate-100">{value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status pie chart */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  dataKey="value"
                  label={({ name, percent }: { name?: string; percent?: number }) =>
                    percent && percent > 0 ? `${name ?? ""} ${(percent * 100).toFixed(0)}%` : ""
                  }
                  labelLine={false}
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell
                      key={index}
                      fill={STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS]}
                    />
                  ))}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Speed histogram */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Speed Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={speedHistogram}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="range" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
                />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Top congested segments table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Top 10 Most Congested Segments</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left border-b border-slate-700">
                  <th className="pb-2 text-slate-400 font-medium">Segment</th>
                  <th className="pb-2 text-slate-400 font-medium">Live Speed</th>
                  <th className="pb-2 text-slate-400 font-medium">Limit</th>
                  <th className="pb-2 text-slate-400 font-medium">Ratio</th>
                </tr>
              </thead>
              <tbody>
                {topCongested.map((seg, i) => (
                  <tr key={i} className="border-b border-slate-800">
                    <td className="py-2 text-slate-300 capitalize">{seg.name}</td>
                    <td className="py-2 text-slate-300">{seg.speed} km/h</td>
                    <td className="py-2 text-slate-500">{seg.limit} km/h</td>
                    <td className="py-2">
                      <Badge
                        variant={
                          seg.ratio >= 70 ? "success" : seg.ratio >= 40 ? "warning" : "destructive"
                        }
                      >
                        {seg.ratio}%
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

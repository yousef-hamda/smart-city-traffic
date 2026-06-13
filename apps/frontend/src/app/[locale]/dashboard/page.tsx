"use client";

import * as React from "react";
import { useQuery } from "@tanstack/react-query";
import dynamic from "next/dynamic";
import { useTrafficStore } from "@/store/traffic";
import { fetchSegments, fetchGlobalStats, fetchAlerts, isUsingMockData } from "@/lib/api";
import { KPICard } from "@/components/dashboard/kpi-card";
import { AlertsFeed } from "@/components/dashboard/alerts-feed";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

const TrafficMap = dynamic(
  () => import("@/components/dashboard/traffic-map").then((m) => ({ default: m.TrafficMap })),
  {
    ssr: false,
    loading: () => <Skeleton className="w-full rounded-lg" style={{ height: "450px" }} />,
  },
);

export default function DashboardPage() {
  const setSegments = useTrafficStore((s) => s.setSegments);
  const setGlobalStats = useTrafficStore((s) => s.setGlobalStats);
  const addAlert = useTrafficStore((s) => s.addAlert);
  const setUsingMockData = useTrafficStore((s) => s.setUsingMockData);

  const segmentsQuery = useQuery({
    queryKey: ["segments"],
    queryFn: fetchSegments,
    refetchInterval: 30000,
  });

  const statsQuery = useQuery({
    queryKey: ["global-stats"],
    queryFn: fetchGlobalStats,
    refetchInterval: 15000,
  });

  const alertsQuery = useQuery({
    queryKey: ["alerts"],
    queryFn: fetchAlerts,
    refetchInterval: 20000,
  });

  // Sync query results into Zustand store
  React.useEffect(() => {
    if (segmentsQuery.data) {
      setSegments(segmentsQuery.data);
      setUsingMockData(isUsingMockData());
    }
  }, [segmentsQuery.data, setSegments, setUsingMockData]);

  React.useEffect(() => {
    if (statsQuery.data) setGlobalStats(statsQuery.data);
  }, [statsQuery.data, setGlobalStats]);

  React.useEffect(() => {
    if (alertsQuery.data) {
      alertsQuery.data.forEach((a) => addAlert(a));
    }
  }, [alertsQuery.data, addAlert]);

  const segments = useTrafficStore((s) => Object.values(s.segments));
  const stats = useTrafficStore((s) => s.globalStats);
  const usingMock = useTrafficStore((s) => s.usingMockData);
  const alerts = useTrafficStore((s) => s.alerts);
  const unacknowledgedCount = alerts.filter((a) => !a.acknowledged).length;

  const isLoading = segmentsQuery.isLoading || statsQuery.isLoading;

  return (
    <div className="p-6 space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Traffic Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Jerusalem Road Network — Live Monitoring</p>
        </div>
        {usingMock && (
          <Badge variant="warning" className="animate-pulse">
            Demo Data — No Backend
          </Badge>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Avg Speed"
          value={stats?.avg_speed ?? "—"}
          unit="km/h"
          icon="🚗"
          loading={isLoading}
          colorClass="text-indigo-400"
        />
        <KPICard
          title="Active Incidents"
          value={stats?.active_incidents ?? "—"}
          icon="⚠"
          loading={isLoading}
          colorClass="text-red-400"
        />
        <KPICard
          title="Slow Segments"
          value={stats?.segments_slow ?? "—"}
          icon="🔴"
          loading={isLoading}
          colorClass="text-amber-400"
        />
        <KPICard
          title="CO₂ Saved"
          value={stats?.co2_saved ?? "—"}
          unit="kg"
          icon="🌿"
          loading={isLoading}
          colorClass="text-green-400"
        />
      </div>

      {/* Map + Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live map */}
        <Card className="lg:col-span-2">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Live Traffic Map</CardTitle>
          </CardHeader>
          <CardContent className="p-0 px-4 pb-4">
            <div style={{ height: "450px" }}>
              {segmentsQuery.isError ? (
                <div className="flex items-center justify-center h-full text-slate-500">
                  <p>Failed to load map data</p>
                </div>
              ) : (
                <TrafficMap segments={segments} />
              )}
            </div>
          </CardContent>
        </Card>

        {/* Alerts feed */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              Live Alerts
              {unacknowledgedCount > 0 && (
                <Badge variant="destructive" className="text-xs">
                  {unacknowledgedCount}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
            {alertsQuery.isLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : (
              <AlertsFeed />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Segment status legend */}
      <Card>
        <CardContent className="p-4">
          <div className="flex items-center gap-6 text-sm flex-wrap">
            <span className="text-slate-400 font-medium">Legend:</span>
            <div className="flex items-center gap-2">
              <div className="w-4 h-2 rounded bg-green-500" />
              <span className="text-slate-300">Free flow (&gt;70% limit)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-2 rounded bg-amber-500" />
              <span className="text-slate-300">Moderate (40–70%)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-2 rounded bg-red-500" />
              <span className="text-slate-300">Congested (&lt;40%)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

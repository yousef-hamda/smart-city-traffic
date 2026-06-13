"use client";

import * as React from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  BarChart,
  Bar,
  Cell,
} from "recharts";
import { useTrafficStore } from "@/store/traffic";
import {
  fetchSegmentHistory,
  fetchShapContributions,
  fetchPrediction,
  postAiQuery,
} from "@/lib/api";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { getStatusBgClass, formatTimestamp } from "@/lib/utils";

export default function SegmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const segmentId = params.id as string;
  const locale = params.locale as string;

  const segment = useTrafficStore((s) => s.segments[segmentId]);
  const [activeTab, setActiveTab] = React.useState("history");
  const [aiOpen, setAiOpen] = React.useState(false);
  const [aiQuestion, setAiQuestion] = React.useState("");
  const [aiAnswer, setAiAnswer] = React.useState("");
  const [aiLoading, setAiLoading] = React.useState(false);

  const historyQuery = useQuery({
    queryKey: ["segment-history", segmentId],
    queryFn: () => fetchSegmentHistory(segmentId),
    enabled: !!segmentId,
  });

  const shapQuery = useQuery({
    queryKey: ["segment-shap", segmentId],
    queryFn: () => fetchShapContributions(segmentId),
    enabled: !!segmentId,
  });

  const predictionQuery = useQuery({
    queryKey: ["segment-prediction", segmentId],
    queryFn: () => fetchPrediction(segmentId),
    enabled: !!segmentId,
  });

  const historyChartData = React.useMemo(() => {
    if (!historyQuery.data) return [];
    return historyQuery.data.timestamps.map((ts, i) => ({
      time: new Date(ts).getHours() + "h",
      speed: historyQuery.data!.speeds[i],
      status: historyQuery.data!.statuses[i],
    }));
  }, [historyQuery.data]);

  const predictionChartData = React.useMemo(() => {
    if (!predictionQuery.data) return [];
    return predictionQuery.data.confidence_band.map((band, i) => ({
      step: `+${i * 5}m`,
      upper: band.upper,
      lower: band.lower,
      predicted: i === 0 ? predictionQuery.data!.predicted_speed : undefined,
    }));
  }, [predictionQuery.data]);

  async function handleAskAI() {
    if (!aiQuestion.trim()) return;
    setAiLoading(true);
    try {
      const result = await postAiQuery(segmentId, aiQuestion);
      setAiAnswer(result.answer);
    } catch {
      setAiAnswer("Failed to get AI response. Please try again.");
    } finally {
      setAiLoading(false);
    }
  }

  if (!segment) {
    return (
      <div className="p-6">
        <Button variant="ghost" onClick={() => router.push(`/${locale}/dashboard`)}>
          ← Back to Dashboard
        </Button>
        <div className="mt-8 text-center text-slate-500">
          <p>Segment not found. Please go back and select a segment from the map.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => router.push(`/${locale}/dashboard`)}
            className="mb-2"
          >
            ← Back
          </Button>
          <h1 className="text-xl font-bold text-slate-100">{segment.name_en}</h1>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <Badge className={getStatusBgClass(segment.status)}>{segment.status}</Badge>
            <span className="text-sm text-slate-400">
              {segment.live_speed} / {segment.speed_limit} km/h
            </span>
            <span className="text-xs text-slate-500">ID: {segment.id}</span>
          </div>
        </div>
        <Button onClick={() => setAiOpen(true)} className="shrink-0">
          Ask AI Assistant
        </Button>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="history">Speed History</TabsTrigger>
          <TabsTrigger value="prediction">Prediction</TabsTrigger>
          <TabsTrigger value="shap">AI Explainability</TabsTrigger>
        </TabsList>

        {/* History chart */}
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">24h Speed History</CardTitle>
            </CardHeader>
            <CardContent>
              {historyQuery.isLoading ? (
                <Skeleton className="h-64 w-full" />
              ) : (
                <ResponsiveContainer width="100%" height={256}>
                  <LineChart data={historyChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
                      labelStyle={{ color: "#e2e8f0" }}
                    />
                    <ReferenceLine
                      y={segment.speed_limit}
                      stroke="#f59e0b"
                      strokeDasharray="4 4"
                      label={{ value: "limit", fill: "#f59e0b", fontSize: 10 }}
                    />
                    <Line
                      type="monotone"
                      dataKey="speed"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Prediction chart */}
        <TabsContent value="prediction">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-3">
                Speed Prediction — Next 60 Minutes
                {predictionQuery.data && (
                  <Badge variant="secondary">
                    Confidence: {Math.round(predictionQuery.data.confidence * 100)}%
                  </Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {predictionQuery.isLoading ? (
                <Skeleton className="h-64 w-full" />
              ) : (
                <ResponsiveContainer width="100%" height={256}>
                  <LineChart data={predictionChartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="step" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 11 }} />
                    <Tooltip
                      contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="upper"
                      stroke="#22c55e"
                      strokeDasharray="4 4"
                      strokeWidth={1}
                      dot={false}
                      name="Upper bound"
                    />
                    <Line
                      type="monotone"
                      dataKey="lower"
                      stroke="#ef4444"
                      strokeDasharray="4 4"
                      strokeWidth={1}
                      dot={false}
                      name="Lower bound"
                    />
                  </LineChart>
                </ResponsiveContainer>
              )}
              {predictionQuery.data && (
                <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
                  <p className="text-sm text-slate-300">
                    Predicted speed in 60 min:{" "}
                    <span className="font-bold text-indigo-400">
                      {predictionQuery.data.predicted_speed} km/h
                    </span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    Last updated: {formatTimestamp(predictionQuery.data.timestamp)}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* SHAP explainability */}
        <TabsContent value="shap">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Feature Importance (SHAP)</CardTitle>
            </CardHeader>
            <CardContent>
              {shapQuery.isLoading ? (
                <Skeleton className="h-64 w-full" />
              ) : shapQuery.data ? (
                <div className="space-y-4">
                  <ResponsiveContainer width="100%" height={200}>
                    <BarChart
                      data={shapQuery.data}
                      layout="vertical"
                      margin={{ left: 120, right: 20, top: 5, bottom: 5 }}
                    >
                      <XAxis type="number" stroke="#94a3b8" tick={{ fontSize: 11 }} />
                      <YAxis
                        type="category"
                        dataKey="feature"
                        stroke="#94a3b8"
                        tick={{ fontSize: 11 }}
                        width={120}
                      />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }}
                      />
                      <Bar dataKey="impact" radius={[0, 4, 4, 0]}>
                        {shapQuery.data.map((entry, index) => (
                          <Cell key={index} fill={entry.impact >= 0 ? "#22c55e" : "#ef4444"} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  <p className="text-xs text-slate-500">
                    Positive values indicate features that increase predicted speed; negative values
                    decrease it.
                  </p>
                </div>
              ) : (
                <p className="text-slate-500">No SHAP data available.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* AI Assistant Sheet */}
      <Sheet open={aiOpen} onOpenChange={setAiOpen}>
        <SheetContent open={aiOpen} onClose={() => setAiOpen(false)}>
          <SheetHeader>
            <SheetTitle>AI Traffic Assistant</SheetTitle>
          </SheetHeader>
          <div className="space-y-4">
            <p className="text-sm text-slate-400">
              Ask a question about <span className="text-slate-200">{segment.name_en}</span>
            </p>
            <textarea
              value={aiQuestion}
              onChange={(e) => setAiQuestion(e.target.value)}
              placeholder="e.g. Why is this segment congested? What time is best to avoid traffic?"
              className="w-full h-24 bg-slate-800 border border-slate-700 rounded-lg p-3 text-sm text-slate-100 placeholder:text-slate-500 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <Button onClick={handleAskAI} disabled={aiLoading || !aiQuestion.trim()}>
              {aiLoading ? "Analyzing..." : "Ask AI"}
            </Button>
            {aiAnswer && (
              <div className="p-4 bg-slate-800/60 rounded-lg border border-slate-700">
                <p className="text-xs text-slate-500 mb-2">AI Response:</p>
                <p className="text-sm text-slate-200 leading-relaxed">{aiAnswer}</p>
              </div>
            )}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}

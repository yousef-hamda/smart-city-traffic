"use client";

import { useState } from "react";

interface ApiKey {
  id: string;
  name: string;
  key: string;
  scopes: string[];
  quota: number;
  used: number;
  createdAt: string;
  lastUsedAt: string | null;
}

interface UsageRow {
  endpoint: string;
  calls: number;
  errors: number;
  avgLatencyMs: number;
  lastCalled: string;
}

const MOCK_USAGE: UsageRow[] = [
  {
    endpoint: "GET /api/v1/segments",
    calls: 1_240,
    errors: 3,
    avgLatencyMs: 42,
    lastCalled: "2025-06-11T08:30:00Z",
  },
  {
    endpoint: "GET /api/v1/alerts",
    calls: 580,
    errors: 1,
    avgLatencyMs: 38,
    lastCalled: "2025-06-11T08:28:00Z",
  },
  {
    endpoint: "POST /api/v1/assistant/chat",
    calls: 95,
    errors: 0,
    avgLatencyMs: 820,
    lastCalled: "2025-06-11T07:55:00Z",
  },
  {
    endpoint: "GET /api/v1/incidents",
    calls: 312,
    errors: 2,
    avgLatencyMs: 55,
    lastCalled: "2025-06-11T08:15:00Z",
  },
];

const SCOPES = [
  "segments:read",
  "incidents:read",
  "alerts:read",
  "predictions:read",
  "assistant:chat",
];

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function KeyCard({ apiKey, onRevoke }: { apiKey: ApiKey; onRevoke: (id: string) => void }) {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);

  const displayKey = revealed
    ? apiKey.key
    : `${apiKey.key.slice(0, 8)}${"•".repeat(24)}${apiKey.key.slice(-4)}`;

  function handleCopy() {
    void navigator.clipboard.writeText(apiKey.key).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }

  const usagePct = Math.round((apiKey.used / apiKey.quota) * 100);

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-800/40 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-semibold text-slate-100">{apiKey.name}</p>
          <p className="mt-0.5 text-xs text-slate-500">
            Created {formatDate(apiKey.createdAt)}
            {apiKey.lastUsedAt !== null && <> · Last used {formatDate(apiKey.lastUsedAt)}</>}
          </p>
        </div>
        <button
          onClick={() => onRevoke(apiKey.id)}
          className="rounded-md border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-medium text-rose-400 transition-colors hover:bg-rose-500/20"
        >
          Revoke
        </button>
      </div>

      {/* Key display */}
      <div className="mt-3 flex items-center gap-2 overflow-hidden rounded-lg bg-slate-900 px-3 py-2.5">
        <code className="flex-1 truncate font-mono text-xs text-slate-300">{displayKey}</code>
        <button
          onClick={() => setRevealed((v) => !v)}
          className="shrink-0 rounded px-2 py-0.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          {revealed ? "Hide" : "Show"}
        </button>
        <button
          onClick={handleCopy}
          className="shrink-0 rounded bg-indigo-600/30 px-2 py-0.5 text-xs text-indigo-300 hover:bg-indigo-600/50 transition-colors"
        >
          {copied ? "Copied!" : "Copy"}
        </button>
      </div>

      {/* Scopes */}
      <div className="mt-3 flex flex-wrap gap-1.5">
        {apiKey.scopes.map((s) => (
          <span
            key={s}
            className="rounded border border-indigo-500/30 bg-indigo-500/10 px-2 py-0.5 text-xs font-mono text-indigo-300"
          >
            {s}
          </span>
        ))}
      </div>

      {/* Quota bar */}
      <div className="mt-4">
        <div className="flex justify-between text-xs text-slate-400">
          <span>Monthly quota</span>
          <span>
            {apiKey.used.toLocaleString()} / {apiKey.quota.toLocaleString()} calls ({usagePct}%)
          </span>
        </div>
        <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-700">
          <div
            className={`h-full rounded-full transition-all ${
              usagePct > 90 ? "bg-rose-500" : usagePct > 70 ? "bg-amber-500" : "bg-indigo-500"
            }`}
            style={{ width: `${usagePct}%` }}
          />
        </div>
      </div>
    </div>
  );
}

export default function KeysClient() {
  const [keys, setKeys] = useState<ApiKey[]>([]);
  const [newKeyName, setNewKeyName] = useState("");
  const [selectedScopes, setSelectedScopes] = useState<string[]>(["segments:read", "alerts:read"]);
  const [generatedKey, setGeneratedKey] = useState<string | null>(null);
  const [copiedNew, setCopiedNew] = useState(false);

  function toggleScope(scope: string) {
    setSelectedScopes((prev) =>
      prev.includes(scope) ? prev.filter((s) => s !== scope) : [...prev, scope],
    );
  }

  function generateKey() {
    if (selectedScopes.length === 0) return;
    const name = newKeyName.trim() || `Key ${keys.length + 1}`;
    const raw = `sct_${crypto.randomUUID().replace(/-/g, "")}`;
    setGeneratedKey(raw);
    const newKey: ApiKey = {
      id: crypto.randomUUID(),
      name,
      key: raw,
      scopes: [...selectedScopes],
      quota: 10_000,
      used: 0,
      createdAt: new Date().toISOString(),
      lastUsedAt: null,
    };
    setKeys((prev) => [newKey, ...prev]);
    setNewKeyName("");
  }

  function revokeKey(id: string) {
    setKeys((prev) => prev.filter((k) => k.id !== id));
    setGeneratedKey(null);
  }

  function copyGenerated() {
    if (generatedKey === null) return;
    void navigator.clipboard.writeText(generatedKey).then(() => {
      setCopiedNew(true);
      setTimeout(() => setCopiedNew(false), 2000);
    });
  }

  return (
    <div>
      {/* Notice banner */}
      <div className="mb-8 rounded-lg border border-amber-500/30 bg-amber-500/10 p-4">
        <p className="text-sm text-amber-300">
          <strong>UI mock</strong> — backend key management pending. Keys generated here are
          client-side only and are not validated by any service.
        </p>
      </div>

      {/* Generate key form */}
      <section className="mb-10 rounded-xl border border-slate-700/60 bg-slate-800/40 p-6">
        <h2 className="mb-4 text-lg font-semibold text-slate-100">Generate API Key</h2>

        <div className="space-y-4">
          {/* Name input */}
          <div>
            <label htmlFor="key-name" className="mb-1.5 block text-sm font-medium text-slate-300">
              Key name
            </label>
            <input
              id="key-name"
              type="text"
              placeholder="e.g. My Dashboard App"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
              className="w-full max-w-sm rounded-lg border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Scope selection */}
          <div>
            <p className="mb-2 text-sm font-medium text-slate-300">Scopes</p>
            <div className="flex flex-wrap gap-2">
              {SCOPES.map((scope) => (
                <button
                  key={scope}
                  onClick={() => toggleScope(scope)}
                  className={[
                    "rounded-full border px-3 py-1 font-mono text-xs transition-colors",
                    selectedScopes.includes(scope)
                      ? "border-indigo-500/60 bg-indigo-500/20 text-indigo-300"
                      : "border-slate-600/50 bg-slate-800 text-slate-400 hover:border-slate-500",
                  ].join(" ")}
                >
                  {scope}
                </button>
              ))}
            </div>
          </div>

          {/* Generate button */}
          <button
            onClick={generateKey}
            disabled={selectedScopes.length === 0}
            className="rounded-lg bg-indigo-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-40"
          >
            Generate Key
          </button>
        </div>

        {/* One-time reveal */}
        {generatedKey !== null && (
          <div className="mt-5 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-4">
            <p className="mb-2 text-sm font-semibold text-emerald-400">
              Your new API key — copy it now, it will not be shown again.
            </p>
            <div className="flex items-center gap-3 overflow-hidden rounded-lg bg-slate-900 px-3 py-2.5">
              <code className="flex-1 truncate font-mono text-sm text-emerald-300">
                {generatedKey}
              </code>
              <button
                onClick={copyGenerated}
                className="shrink-0 rounded bg-emerald-600/30 px-3 py-1 text-xs font-medium text-emerald-300 hover:bg-emerald-600/50 transition-colors"
              >
                {copiedNew ? "Copied!" : "Copy"}
              </button>
            </div>
          </div>
        )}
      </section>

      {/* Keys list */}
      <section className="mb-10">
        <h2 className="mb-4 text-lg font-semibold text-slate-100">Active Keys ({keys.length})</h2>
        {keys.length === 0 ? (
          <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center">
            <p className="text-slate-500">No keys yet. Generate one above to get started.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {keys.map((k) => (
              <KeyCard key={k.id} apiKey={k} onRevoke={revokeKey} />
            ))}
          </div>
        )}
      </section>

      {/* Usage table */}
      <section>
        <h2 className="mb-4 text-lg font-semibold text-slate-100">Usage Breakdown (mock)</h2>
        <div className="overflow-hidden rounded-xl border border-slate-700/60">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/60">
              <tr>
                {["Endpoint", "Calls", "Errors", "Avg Latency", "Last Called"].map((h) => (
                  <th
                    key={h}
                    className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/40">
              {MOCK_USAGE.map((row) => (
                <tr
                  key={row.endpoint}
                  className="bg-slate-800/20 transition-colors hover:bg-slate-800/40"
                >
                  <td className="px-4 py-3 font-mono text-xs text-slate-200">{row.endpoint}</td>
                  <td className="px-4 py-3 text-slate-300">{row.calls.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    <span className={row.errors > 0 ? "text-rose-400" : "text-slate-500"}>
                      {row.errors}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-300">{row.avgLatencyMs} ms</td>
                  <td className="px-4 py-3 text-slate-400">{formatDate(row.lastCalled)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

import { apiGroups } from "@/src/lib/api-catalog";
import type { ApiEndpoint, ApiGroup } from "@/src/lib/api-catalog";

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30",
  POST: "bg-blue-500/20 text-blue-300 border-blue-500/30",
  PUT: "bg-amber-500/20 text-amber-300 border-amber-500/30",
  PATCH: "bg-orange-500/20 text-orange-300 border-orange-500/30",
  DELETE: "bg-rose-500/20 text-rose-300 border-rose-500/30",
};

const GROUP_ACCENT: Record<string, string> = {
  auth: "border-l-indigo-500",
  segments: "border-l-violet-500",
  incidents: "border-l-rose-500",
  alerts: "border-l-amber-500",
  predictions: "border-l-emerald-500",
  assistant: "border-l-sky-500",
};

function MethodBadge({ method }: { method: string }) {
  const cls = METHOD_COLORS[method] ?? "bg-slate-500/20 text-slate-300 border-slate-500/30";
  return (
    <span
      className={`inline-flex items-center rounded border px-1.5 py-0.5 font-mono text-xs font-semibold ${cls}`}
    >
      {method}
    </span>
  );
}

function AuthBadge({ auth }: { auth: string }) {
  if (auth === "none") return null;
  return (
    <span className="inline-flex items-center rounded border border-slate-600/50 bg-slate-800/60 px-1.5 py-0.5 text-xs text-slate-400">
      {auth === "jwt" ? "JWT" : "API Key"}
    </span>
  );
}

function EndpointCard({ endpoint }: { endpoint: ApiEndpoint }) {
  return (
    <div className="group rounded-lg border border-slate-700/50 bg-slate-800/40 p-4 transition-colors hover:border-slate-600/60 hover:bg-slate-800/60">
      <div className="flex flex-wrap items-center gap-2">
        <MethodBadge method={endpoint.method} />
        <code className="flex-1 font-mono text-sm text-slate-200">{endpoint.path}</code>
        <AuthBadge auth={endpoint.auth} />
      </div>
      <p className="mt-2 text-sm text-slate-400">{endpoint.description}</p>
      {endpoint.roles !== undefined && endpoint.roles.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {endpoint.roles.map((role) => (
            <span
              key={role}
              className="rounded border border-violet-500/30 bg-violet-500/10 px-1.5 py-0.5 text-xs text-violet-300"
            >
              {role}
            </span>
          ))}
        </div>
      )}
      {endpoint.params.length > 0 && (
        <div className="mt-3 space-y-1">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">
            Parameters
          </p>
          <div className="grid gap-1">
            {endpoint.params.map((p) => (
              <div key={p.name} className="flex flex-wrap items-baseline gap-x-2 text-xs">
                <code className="font-mono font-medium text-slate-300">{p.name}</code>
                <span className="text-slate-500">{p.type}</span>
                <span className="rounded bg-slate-700/50 px-1 text-slate-400">{p.location}</span>
                {p.required && <span className="text-rose-400">required</span>}
                <span className="text-slate-500">{p.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function GroupSection({ group }: { group: ApiGroup }) {
  const accentClass = GROUP_ACCENT[group.group] ?? "border-l-slate-500";
  return (
    <section id={group.group} className="scroll-mt-20">
      <div className={`mb-4 border-l-4 pl-4 ${accentClass}`}>
        <h2 className="text-lg font-semibold text-slate-100">{group.label}</h2>
        <p className="mt-0.5 text-sm text-slate-400">{group.description}</p>
      </div>
      <div className="space-y-3">
        {group.endpoints.map((ep) => (
          <EndpointCard key={ep.id} endpoint={ep} />
        ))}
      </div>
    </section>
  );
}

export default function CatalogPage() {
  const totalEndpoints = apiGroups.reduce((n, g) => n + g.endpoints.length, 0);

  return (
    <div>
      {/* Hero */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100 sm:text-4xl">
          API Catalog
        </h1>
        <p className="mt-3 max-w-2xl text-base text-slate-400">
          Complete reference for the Smart City Traffic REST API. Authenticate once with JWT, then
          explore <span className="font-semibold text-indigo-400">{totalEndpoints} endpoints</span>{" "}
          across {apiGroups.length} resource groups.
        </p>

        {/* Stats row */}
        <div className="mt-6 flex flex-wrap gap-4">
          {apiGroups.map((g) => (
            <a
              key={g.group}
              href={`#${g.group}`}
              className="flex items-center gap-2 rounded-lg border border-slate-700/50 bg-slate-800/40 px-4 py-2.5 text-sm transition-colors hover:border-slate-600/60 hover:bg-slate-800/60"
            >
              <span className="font-medium text-slate-200">{g.label}</span>
              <span className="rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-400">
                {g.endpoints.length}
              </span>
            </a>
          ))}
        </div>
      </div>

      {/* Base URL callout */}
      <div className="mb-8 rounded-lg border border-indigo-500/20 bg-indigo-500/5 p-4">
        <p className="text-sm text-slate-300">
          <span className="font-semibold text-indigo-400">Base URL: </span>
          <code className="font-mono text-slate-200">http://localhost:3000</code>
          <span className="ml-4 text-slate-500">
            All endpoints require{" "}
            <code className="font-mono text-slate-400">Authorization: Bearer &lt;token&gt;</code>{" "}
            unless marked public.
          </span>
        </p>
      </div>

      {/* Endpoint groups */}
      <div className="space-y-12">
        {apiGroups.map((g) => (
          <GroupSection key={g.group} group={g} />
        ))}
      </div>
    </div>
  );
}

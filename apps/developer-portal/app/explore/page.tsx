import { graphqlQueries } from "@/src/lib/api-catalog";
import SwaggerPanel from "./SwaggerPanel";

const GRAPHQL_SDL = `# Smart City Traffic — GraphQL Federated Schema (excerpt)

type Segment @key(fields: "id") {
  id: ID!
  name: String!
  congestionLevel: Float!
  avgSpeed: Float!
  vehicleCount: Int
  status: SegmentStatus!
  geometry: GeoJSON
  updatedAt: DateTime!
  latestPrediction: Prediction
  incidents(limit: Int): [Incident!]!
}

type Incident @key(fields: "id") {
  id: ID!
  type: String!
  severity: Severity!
  description: String!
  detectedAt: DateTime!
  resolvedAt: DateTime
  location: LatLng!
  segment: Segment
}

type Alert @key(fields: "id") {
  id: ID!
  rule: String!
  severity: Severity!
  message: String!
  acknowledged: Boolean!
  createdAt: DateTime!
  segment: Segment
}

type Prediction {
  segmentId: ID!
  horizon: Int!
  predictedCongestion: Float!
  predictedSpeed: Float!
  confidence: Float!
  model: String!
  generatedAt: DateTime!
}

type LatLng {
  lat: Float!
  lng: Float!
}

enum SegmentStatus { FREE SLOW CONGESTED }
enum Severity { LOW MEDIUM HIGH CRITICAL }

scalar DateTime
scalar GeoJSON

type Query {
  segment(id: ID!): Segment
  segments(page: Int, limit: Int, status: SegmentStatus): SegmentPage!
  incidents(filter: IncidentFilter, orderBy: IncidentOrder): [Incident!]!
  alerts(limit: Int, orderBy: AlertOrder): [Alert!]!
}

type Mutation {
  acknowledgeAlert(id: ID!): Alert!
}

type Subscription {
  segmentUpdated: Segment!
  incidentCreated: Incident!
  alertFired: Alert!
}

type SegmentPage {
  data: [Segment!]!
  meta: PageMeta!
}

type PageMeta {
  page: Int!
  limit: Int!
  total: Int!
}

input IncidentFilter {
  resolvedAt: DateTime
  severity: Severity
  segmentId: ID
}

input IncidentOrder {
  detectedAt: SortDir
}

input AlertOrder {
  createdAt: SortDir
}

enum SortDir { ASC DESC }`;

export default function ExplorePage() {
  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight text-slate-100 sm:text-4xl">
          Interactive Explorer
        </h1>
        <p className="mt-3 max-w-2xl text-base text-slate-400">
          Test REST endpoints directly in the browser via Swagger UI, or inspect the GraphQL
          federated schema below. When the API gateway is running, point GraphQL clients at{" "}
          <code className="font-mono text-indigo-300">http://localhost:3000/graphql</code>.
        </p>
      </div>

      {/* REST Explorer */}
      <section className="mb-14">
        <h2 className="mb-4 text-xl font-semibold text-slate-100">REST API — Swagger UI</h2>
        <p className="mb-4 text-sm text-slate-400">
          Expand any endpoint, fill in parameters, and click{" "}
          <strong className="text-slate-300">Execute</strong>. Requests are sent from your browser —
          make sure the API gateway is reachable at localhost:3000.
        </p>
        <SwaggerPanel />
      </section>

      {/* GraphQL schema */}
      <section>
        <h2 className="mb-4 text-xl font-semibold text-slate-100">GraphQL Federated Schema</h2>
        <p className="mb-4 text-sm text-slate-400">
          The gateway exposes a federated GraphQL endpoint at{" "}
          <code className="font-mono text-indigo-300">http://localhost:3000/graphql</code>. Below is
          the combined SDL for reference.
        </p>

        <div className="mb-8 overflow-hidden rounded-xl border border-slate-700/60 bg-slate-900">
          <div className="border-b border-slate-700/60 bg-slate-800/50 px-4 py-2.5">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Schema Definition Language (SDL)
            </span>
          </div>
          <textarea
            readOnly
            value={GRAPHQL_SDL}
            className="h-96 w-full resize-none bg-transparent p-4 font-mono text-xs text-slate-300 focus:outline-none"
            spellCheck={false}
          />
        </div>

        {/* Example queries */}
        <h3 className="mb-3 text-lg font-semibold text-slate-200">Example Queries</h3>
        <div className="grid gap-4 sm:grid-cols-2">
          {graphqlQueries.map((q) => (
            <div key={q.name} className="rounded-xl border border-slate-700/60 bg-slate-800/40 p-4">
              <p className="mb-1 text-sm font-semibold text-indigo-300">{q.name}</p>
              <p className="mb-3 text-xs text-slate-400">{q.description}</p>
              <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs leading-relaxed text-slate-300">
                <code>{q.query}</code>
              </pre>
              {q.variables !== undefined && (
                <div className="mt-2">
                  <p className="mb-1 text-xs font-medium text-slate-500">Variables</p>
                  <pre className="overflow-x-auto rounded bg-slate-900 p-2 text-xs text-slate-400">
                    <code>{JSON.stringify(q.variables, null, 2)}</code>
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

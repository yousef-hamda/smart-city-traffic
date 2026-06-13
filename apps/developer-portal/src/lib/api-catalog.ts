export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type ParamLocation = "path" | "query" | "body" | "header";

export interface EndpointParam {
  name: string;
  location: ParamLocation;
  type: string;
  required: boolean;
  description: string;
}

export interface ApiEndpoint {
  id: string;
  method: HttpMethod;
  path: string;
  description: string;
  auth: "none" | "jwt" | "apikey";
  roles?: string[];
  params: EndpointParam[];
  sampleResponse: unknown;
}

export type EndpointGroup =
  | "auth"
  | "segments"
  | "incidents"
  | "alerts"
  | "predictions"
  | "assistant";

export interface ApiGroup {
  group: EndpointGroup;
  label: string;
  description: string;
  color: string;
  endpoints: ApiEndpoint[];
}

export interface GraphqlQuery {
  name: string;
  description: string;
  query: string;
  variables?: Record<string, unknown>;
}

export const apiGroups: ApiGroup[] = [
  {
    group: "auth",
    label: "Authentication",
    description: "Register, login, token refresh, and user profile endpoints.",
    color: "indigo",
    endpoints: [
      {
        id: "auth-register",
        method: "POST",
        path: "/api/v1/auth/register",
        description: "Register a new user account.",
        auth: "none",
        params: [
          {
            name: "email",
            location: "body",
            type: "string",
            required: true,
            description: "User email address",
          },
          {
            name: "password",
            location: "body",
            type: "string",
            required: true,
            description: "Password (min 8 chars)",
          },
          {
            name: "name",
            location: "body",
            type: "string",
            required: true,
            description: "Display name",
          },
        ],
        sampleResponse: {
          id: "usr_01hx...",
          email: "dev@example.com",
          name: "Jane Dev",
          role: "viewer",
          createdAt: "2025-01-15T10:00:00Z",
        },
      },
      {
        id: "auth-login",
        method: "POST",
        path: "/api/v1/auth/login",
        description: "Authenticate with email and password; receive JWT tokens.",
        auth: "none",
        params: [
          {
            name: "email",
            location: "body",
            type: "string",
            required: true,
            description: "Registered email",
          },
          {
            name: "password",
            location: "body",
            type: "string",
            required: true,
            description: "Account password",
          },
        ],
        sampleResponse: {
          accessToken: "eyJhbGciOiJSUzI1NiJ9...",
          refreshToken: "dGhpcyBpcyBhIHJlZnJlc2g...",
          expiresIn: 3600,
        },
      },
      {
        id: "auth-refresh",
        method: "POST",
        path: "/api/v1/auth/refresh",
        description: "Exchange a refresh token for a new access token.",
        auth: "none",
        params: [
          {
            name: "refreshToken",
            location: "body",
            type: "string",
            required: true,
            description: "Valid refresh token",
          },
        ],
        sampleResponse: {
          accessToken: "eyJhbGciOiJSUzI1NiJ9.new...",
          expiresIn: 3600,
        },
      },
      {
        id: "auth-logout",
        method: "POST",
        path: "/api/v1/auth/logout",
        description: "Invalidate the current session tokens.",
        auth: "jwt",
        params: [],
        sampleResponse: { message: "Logged out successfully" },
      },
      {
        id: "auth-me",
        method: "GET",
        path: "/api/v1/auth/me",
        description: "Retrieve the authenticated user's profile.",
        auth: "jwt",
        params: [],
        sampleResponse: {
          id: "usr_01hx...",
          email: "dev@example.com",
          name: "Jane Dev",
          role: "analyst",
          createdAt: "2025-01-15T10:00:00Z",
        },
      },
    ],
  },
  {
    group: "segments",
    label: "Road Segments",
    description: "Query live traffic data for individual road segments.",
    color: "violet",
    endpoints: [
      {
        id: "segments-list",
        method: "GET",
        path: "/api/v1/segments",
        description: "Paginated list of road segments with current traffic metrics.",
        auth: "jwt",
        params: [
          {
            name: "page",
            location: "query",
            type: "number",
            required: false,
            description: "Page number (default 1)",
          },
          {
            name: "limit",
            location: "query",
            type: "number",
            required: false,
            description: "Items per page (default 20, max 100)",
          },
          {
            name: "status",
            location: "query",
            type: "string",
            required: false,
            description: "Filter by status: free | slow | congested",
          },
        ],
        sampleResponse: {
          data: [
            {
              id: "seg_001",
              name: "Main St — 1st to 5th Ave",
              congestionLevel: 0.72,
              avgSpeed: 18,
              status: "slow",
              updatedAt: "2025-06-11T08:32:00Z",
            },
          ],
          meta: { page: 1, limit: 20, total: 340 },
        },
      },
      {
        id: "segments-by-id",
        method: "GET",
        path: "/api/v1/segments/:id",
        description: "Detailed traffic data for a single road segment.",
        auth: "jwt",
        params: [
          {
            name: "id",
            location: "path",
            type: "string",
            required: true,
            description: "Segment ID",
          },
        ],
        sampleResponse: {
          id: "seg_001",
          name: "Main St — 1st to 5th Ave",
          congestionLevel: 0.72,
          avgSpeed: 18,
          vehicleCount: 412,
          status: "slow",
          geometry: {
            type: "LineString",
            coordinates: [
              [-74.006, 40.7128],
              [-74.005, 40.7135],
            ],
          },
          updatedAt: "2025-06-11T08:32:00Z",
        },
      },
    ],
  },
  {
    group: "incidents",
    label: "Incidents",
    description: "Access traffic incidents detected by CV and sensor fusion.",
    color: "rose",
    endpoints: [
      {
        id: "incidents-list",
        method: "GET",
        path: "/api/v1/incidents",
        description:
          "List active and recent traffic incidents. Requires admin, analyst, or viewer role.",
        auth: "jwt",
        roles: ["admin", "analyst", "viewer"],
        params: [
          {
            name: "severity",
            location: "query",
            type: "string",
            required: false,
            description: "Filter: low | medium | high | critical",
          },
          {
            name: "from",
            location: "query",
            type: "string",
            required: false,
            description: "ISO-8601 start timestamp",
          },
          {
            name: "to",
            location: "query",
            type: "string",
            required: false,
            description: "ISO-8601 end timestamp",
          },
        ],
        sampleResponse: {
          data: [
            {
              id: "inc_9k2m",
              type: "accident",
              severity: "high",
              segmentId: "seg_042",
              description: "Multi-vehicle collision blocking 2 lanes",
              detectedAt: "2025-06-11T07:55:00Z",
              resolvedAt: null,
              location: { lat: 40.7148, lng: -74.009 },
            },
          ],
          total: 14,
        },
      },
    ],
  },
  {
    group: "alerts",
    label: "Alerts",
    description: "Rule-based alerts triggered by threshold breaches.",
    color: "amber",
    endpoints: [
      {
        id: "alerts-list",
        method: "GET",
        path: "/api/v1/alerts",
        description: "Paginated list of system alerts with severity and status.",
        auth: "jwt",
        params: [
          {
            name: "page",
            location: "query",
            type: "number",
            required: false,
            description: "Page number",
          },
          {
            name: "limit",
            location: "query",
            type: "number",
            required: false,
            description: "Items per page (max 50)",
          },
          {
            name: "acknowledged",
            location: "query",
            type: "boolean",
            required: false,
            description: "Filter acknowledged state",
          },
        ],
        sampleResponse: {
          data: [
            {
              id: "alrt_7zx1",
              rule: "congestion_threshold",
              severity: "medium",
              message: "Congestion on seg_001 exceeded 70% for >5 min",
              segmentId: "seg_001",
              acknowledged: false,
              createdAt: "2025-06-11T08:30:00Z",
            },
          ],
          meta: { page: 1, limit: 20, total: 3 },
        },
      },
    ],
  },
  {
    group: "predictions",
    label: "Predictions (ML)",
    description: "Traffic flow predictions from LSTM/Transformer models.",
    color: "emerald",
    endpoints: [
      {
        id: "predictions-segment",
        method: "GET",
        path: "/api/v1/predictions/:segmentId",
        description: "15-minute ahead traffic prediction for a segment.",
        auth: "jwt",
        params: [
          {
            name: "segmentId",
            location: "path",
            type: "string",
            required: true,
            description: "Road segment ID",
          },
          {
            name: "horizon",
            location: "query",
            type: "number",
            required: false,
            description: "Horizon in minutes (5–60, default 15)",
          },
        ],
        sampleResponse: {
          segmentId: "seg_001",
          horizon: 15,
          predictedCongestion: 0.81,
          predictedSpeed: 14,
          confidence: 0.87,
          model: "transformer-v3",
          generatedAt: "2025-06-11T08:32:01Z",
        },
      },
    ],
  },
  {
    group: "assistant",
    label: "AI Assistant",
    description: "Natural language traffic queries via the AI assistant service.",
    color: "sky",
    endpoints: [
      {
        id: "assistant-chat",
        method: "POST",
        path: "/api/v1/assistant/chat",
        description: "Send a natural-language query; receive a structured response.",
        auth: "jwt",
        params: [
          {
            name: "message",
            location: "body",
            type: "string",
            required: true,
            description: "User message",
          },
          {
            name: "sessionId",
            location: "body",
            type: "string",
            required: false,
            description: "Conversation session ID for context continuity",
          },
        ],
        sampleResponse: {
          sessionId: "sess_abc123",
          reply:
            "The heaviest congestion right now is on Main St (seg_001) with 72% congestion level. An incident was detected at 07:55.",
          citations: ["seg_001", "inc_9k2m"],
          generatedAt: "2025-06-11T08:32:05Z",
        },
      },
    ],
  },
];

export const graphqlQueries: GraphqlQuery[] = [
  {
    name: "LiveSegments",
    description: "Stream real-time congestion data for all segments.",
    query: `subscription LiveSegments {
  segmentUpdated {
    id
    name
    congestionLevel
    avgSpeed
    status
    updatedAt
  }
}`,
  },
  {
    name: "SegmentDetail",
    description: "Full detail query for a single segment including predictions.",
    query: `query SegmentDetail($id: ID!) {
  segment(id: $id) {
    id
    name
    congestionLevel
    avgSpeed
    vehicleCount
    geometry {
      type
      coordinates
    }
    latestPrediction {
      predictedCongestion
      predictedSpeed
      horizon
      confidence
    }
    incidents(limit: 5) {
      id
      type
      severity
      detectedAt
    }
  }
}`,
    variables: { id: "seg_001" },
  },
  {
    name: "ActiveIncidents",
    description: "List all unresolved incidents with location data.",
    query: `query ActiveIncidents {
  incidents(filter: { resolvedAt: null }, orderBy: { detectedAt: DESC }) {
    id
    type
    severity
    description
    detectedAt
    location {
      lat
      lng
    }
    segment {
      id
      name
    }
  }
}`,
  },
  {
    name: "AlertsFeed",
    description: "Recent alerts with acknowledgement state.",
    query: `query AlertsFeed($limit: Int = 20) {
  alerts(limit: $limit, orderBy: { createdAt: DESC }) {
    id
    rule
    severity
    message
    acknowledged
    createdAt
    segment {
      id
      name
    }
  }
}`,
  },
];

export function getEndpointById(id: string): ApiEndpoint | undefined {
  for (const group of apiGroups) {
    const endpoint = group.endpoints.find((e) => e.id === id);
    if (endpoint !== undefined) return endpoint;
  }
  return undefined;
}

export function getAllEndpoints(): ApiEndpoint[] {
  return apiGroups.flatMap((g) => g.endpoints);
}

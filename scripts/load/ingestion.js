// k6 load test: sustain ~10k sensor readings/minute against the ingestion
// bulk endpoint for 1 minute. Run: k6 run scripts/load/ingestion.js
import http from "k6/http";
import { check, sleep } from "k6";

const BASE = __ENV.INGESTION_URL || "http://localhost:8081";

export const options = {
  scenarios: {
    ingest: {
      executor: "constant-arrival-rate",
      rate: 170, // ~170 req/s * batch of 1 ~= 10.2k/min
      timeUnit: "1s",
      duration: "1m",
      preAllocatedVUs: 50,
      maxVUs: 200,
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<500"],
  },
};

function reading() {
  return {
    sensor_id: `S-load-${Math.floor(Math.random() * 147)}`,
    ts: new Date().toISOString(),
    lat: 31.78 + Math.random() * 0.05,
    lon: 35.21 + Math.random() * 0.05,
    vehicle_count: Math.floor(Math.random() * 30),
    avg_speed_kmh: 10 + Math.random() * 50,
    occupancy_pct: Math.random() * 100,
  };
}

export default function () {
  const res = http.post(`${BASE}/api/v1/readings/bulk`, JSON.stringify([reading(), reading()]), {
    headers: { "Content-Type": "application/json" },
  });
  check(res, { "accepted (2xx)": (r) => r.status >= 200 && r.status < 300 });
  sleep(0.1);
}

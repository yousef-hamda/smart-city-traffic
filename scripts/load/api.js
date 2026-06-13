// k6 load test: 500 RPS sustained for 2 minutes against the API gateway's
// read endpoints. Run: k6 run scripts/load/api.js
import http from "k6/http";
import { check } from "k6";

const BASE = __ENV.API_URL || "http://localhost:8080";

export const options = {
  scenarios: {
    reads: {
      executor: "constant-arrival-rate",
      rate: 500,
      timeUnit: "1s",
      duration: "2m",
      preAllocatedVUs: 100,
      maxVUs: 400,
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.01"],
    http_req_duration: ["p(95)<300", "p(99)<800"],
  },
};

const paths = ["/api/v1/segments", "/api/v1/neighborhoods", "/api/v1/alerts", "/health"];

export default function () {
  const path = paths[Math.floor(Math.random() * paths.length)];
  const res = http.get(`${BASE}${path}`);
  check(res, { "2xx": (r) => r.status >= 200 && r.status < 300 });
}

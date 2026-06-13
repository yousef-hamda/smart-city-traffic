// Consumer-driven contract: the API gateway (consumer) depends on the
// ml-prediction service's POST /forecast/demand. This test stands up a Pact
// mock provider, exercises the consumer's expectation against it, and writes a
// pact file the provider verifies in its own CI — so neither side can break the
// contract silently. Runs fully offline.
import path from "node:path";

import { PactV3, MatchersV3 } from "@pact-foundation/pact";
import axios from "axios";

const { like, eachLike, integer, decimal } = MatchersV3;

const provider = new PactV3({
  consumer: "api-gateway",
  provider: "ml-prediction",
  dir: path.resolve(process.cwd(), "pacts"),
});

describe("api-gateway → ml-prediction /forecast/demand", () => {
  it("returns hourly demand for a segment", async () => {
    provider
      .given("segment jaffa-road-00 exists")
      .uponReceiving("a demand forecast request")
      .withRequest({
        method: "POST",
        path: "/forecast/demand",
        headers: { "Content-Type": "application/json" },
        body: { segment_id: "jaffa-road-00", horizon_hours: 6 },
      })
      .willRespondWith({
        status: 200,
        headers: { "Content-Type": "application/json" },
        body: {
          predictions: eachLike({ hour: integer(8), vehicle_count: decimal(42.5) }),
          model_version: like("demand-xgboost-v1"),
        },
      });

    await provider.executeTest(async (mock) => {
      const res = await axios.post(
        `${mock.url}/forecast/demand`,
        { segment_id: "jaffa-road-00", horizon_hours: 6 },
        { headers: { "Content-Type": "application/json" } },
      );
      expect(res.status).toBe(200);
      expect(res.data.predictions.length).toBeGreaterThan(0);
      expect(typeof res.data.model_version).toBe("string");
    });
  });
});

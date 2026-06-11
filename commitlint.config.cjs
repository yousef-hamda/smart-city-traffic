/**
 * Conventional Commits enforced repo-wide.
 * Scopes mirror the monorepo layout so history reads like a changelog.
 */
module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "scope-enum": [
      1,
      "always",
      [
        "frontend",
        "mobile",
        "developer-portal",
        "api-gateway",
        "realtime-gateway",
        "voice-gateway",
        "ai-assistant",
        "sensor-ingestion",
        "vision-service",
        "ml-prediction",
        "rl-optimizer",
        "federated",
        "sensor-simulator",
        "camera-simulator",
        "shared-types",
        "proto",
        "ui",
        "i18n",
        "ml",
        "analytics",
        "flink",
        "neo4j",
        "infra",
        "docs",
        "ci",
        "scripts",
        "repo"
      ]
    ],
    "body-max-line-length": [1, "always", 200]
  }
};

# Security

Defense in depth across identity, secrets, supply chain, and the network.

## Identity & access

- **JWT** access (short-lived) + **rotating refresh** tokens at the API
  gateway; passwords hashed with argon2.
- **RBAC** — `admin` / `analyst` / `viewer` / `citizen`, enforced by a guard
  reading the validated token.
- **API keys** — scoped, per-key **token-bucket rate limiting** (Redis) for the
  developer portal; only a hash is stored, the plaintext key is shown once.
- **Socket auth** — the realtime gateway verifies the gateway's access token on
  the WebSocket handshake (shared secret, no per-connection round trip).

## Secrets (Vault)

Services pull credentials from **HashiCorp Vault** at startup — secrets never
live in images, ConfigMaps, or the repo. Each service has a **least-privilege**
policy (`infra/vault/policies/*.hcl`): read only its own path plus `shared`.
Dev uses `-dev` mode (`infra/vault/seed.sh`); production uses Kubernetes auth +
auto-unseal.

## Supply chain (CI)

- **Trivy** scans every built image and **fails the build on HIGH/CRITICAL**
  CVEs (`ignore-unfixed`).
- **Syft** generates an **SBOM** (SPDX) per image, uploaded as a CI artifact
  and attached to releases.
- **gitleaks** scans the repo + history for committed secrets on every PR.

## Network (Istio)

- **mTLS STRICT** between all in-mesh services (`PeerAuthentication`).
- **Circuit breaking** (outlier detection) + **retry budgets** on hot paths.
- Nothing gRPC or internal is exposed publicly; the API/realtime gateways are
  the only ingress.

## Input validation

Validated at every boundary: **Zod** (TS), **Pydantic** (Python), **Bean
Validation** (Java). Malformed input is rejected with a clean problem response,
never trusted.

## Secrets audit

A scan of the tracked tree (and a CI gitleaks job) confirms:

- **no** committed `.env` files (only `.env.example` templates);
- **no** private keys, AWS keys, or provider tokens in the repo;
- the only credentials present are clearly-labeled **dev-only** placeholders
  (`traffic_dev_password`, `dev-root-token`) used by docker-compose for local
  development — never reused in any real deployment.

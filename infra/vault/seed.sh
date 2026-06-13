#!/usr/bin/env bash
# Seed the dev Vault with the platform's secrets and per-service policies.
# DEV MODE ONLY — the root token and these values are for local use; production
# uses Kubernetes auth, auto-unseal, and real secret material.
set -euo pipefail
export VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-dev-root-token}"

vault secrets enable -path=secret kv-v2 2>/dev/null || true

# Shared secrets
vault kv put secret/shared/postgres \
  url="postgresql://traffic:traffic_dev_password@postgres:5432/traffic"
vault kv put secret/shared/redis url="redis://redis:6379/0"

# Per-service secrets
vault kv put secret/api-gateway/jwt \
  access_secret="$(openssl rand -hex 32)" \
  refresh_secret="$(openssl rand -hex 32)"
vault kv put secret/ml-prediction/mlflow uri="http://mlflow:5000"
vault kv put secret/ai-assistant/anthropic api_key="set-me-in-real-deploys"

# Policies
for p in infra/vault/policies/*.hcl; do
  name="$(basename "$p" .hcl)"
  vault policy write "$name" "$p"
done

echo "Vault seeded: secrets + $(ls infra/vault/policies/*.hcl | wc -l) policies"

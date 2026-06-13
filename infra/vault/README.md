# Vault (secrets)

Services pull credentials from Vault at startup — secrets never live in images,
ConfigMaps, or the repo. Dev runs Vault in `-dev` mode; production uses
Kubernetes auth + auto-unseal.

```bash
docker compose --profile security up -d vault   # dev-mode Vault on :8200
VAULT_TOKEN=dev-root-token bash infra/vault/seed.sh
```

Each service has a **least-privilege policy** (`policies/*.hcl`): read only its
own `secret/data/<service>/*` plus `secret/data/shared/*`. The
[secrets audit](../../docs/security.md) confirms no secret material is committed.

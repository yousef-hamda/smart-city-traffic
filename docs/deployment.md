# Deployment

How the platform goes from a git push to running pods, with safe canary
delivery of the ML service.

## Local (Docker Compose)

```bash
make dev          # full stack with hot reload
make dev-infra    # data/streaming layer only
docker compose --profile analytics up -d        # lakehouse (Flink/Trino/Superset)
docker compose --profile observability up -d     # Prometheus/Grafana/Loki/Tempo
```

## Kubernetes (Helm)

The umbrella chart `infra/helm/smart-city` renders a Deployment + Service per
service from `values.yaml`, a shared ConfigMap, the Istio policies, and the
Argo Rollout for ml-prediction.

```bash
make k8s-up       # helm upgrade --install smart-city infra/helm/smart-city
helm template smart-city infra/helm/smart-city | kubectl apply -f -   # plain-manifest path
```

Plain manifests are also rendered to `infra/k8s/manifests.yaml`.

## Service mesh (Istio)

`templates/istio.yaml` (gated by `istio.enabled`) installs:

- **PeerAuthentication** `STRICT` — mTLS for all in-mesh traffic.
- **DestinationRule** for ml-prediction — connection pooling, **outlier
  detection** (circuit breaking after 5 consecutive 5xx), and the
  `stable`/`canary` subsets.
- **VirtualService** — **retries** with a budget and the weighted route that
  Argo Rollouts shifts during a canary.

## GitOps (ArgoCD app-of-apps)

```
push to main ─► CI builds + pushes images, bumps image tag in infra/ ─►
ArgoCD detects the change ─► syncs the cluster
```

`infra/argocd/app-of-apps.yaml` is the root Application; it manages
`infra/argocd/apps/smart-city.yaml`, which deploys the Helm chart with
automated prune + self-heal.

## Progressive delivery (Argo Rollouts)

`ml-prediction` is delivered as an **Argo Rollout** (not a plain Deployment).
A new model image rolls out by canary steps **10% → 25% → 50% → 100%**, pausing
60s at each step to run an **AnalysisTemplate** that queries Prometheus:

- abort if **p95 latency ≥ 250 ms**, or
- abort if **success rate < 99%**.

On failure the rollout auto-rolls back to `stable`; traffic shifting is done
via the Istio VirtualService weights. This is how new models reach production
without a risky big-bang swap.

## Cloud (Terraform skeleton)

`infra/terraform/` sketches the AWS shape — **EKS** (compute), **RDS Postgres**
(managed Postgres/TimescaleDB), and **MSK** (managed Kafka) — mapping the
compose stack to managed services. It's a reviewed starter: configure remote
state and networking, then `terraform plan` before any apply. Secrets
(`db_password`) come from `TF_VAR_*` / Secrets Manager, never the repo.

# Helm chart — smart-city

Umbrella chart for the platform. Generic templates render a Deployment +
Service per entry in `values.yaml`'s `services` map; `ml-prediction` is
delivered via an Argo Rollout (canary) instead.

```bash
helm lint infra/helm/smart-city
helm template smart-city infra/helm/smart-city          # render
helm upgrade --install smart-city infra/helm/smart-city -n smart-city --create-namespace
```

Toggles: `istio.enabled` (mTLS + retries + circuit breaking + canary subsets),
`rollouts.enabled` (Argo Rollout + AnalysisTemplate for ml-prediction).
See [docs/deployment.md](../../../docs/deployment.md).

# Each service gets a least-privilege policy: read only its own secrets path.
# Services authenticate via Kubernetes auth (prod) or a token (dev) and pull
# credentials at startup — nothing sensitive lives in ConfigMaps or images.
path "secret/data/ml-prediction/*" {
  capabilities = ["read"]
}
path "secret/data/shared/*" {
  capabilities = ["read"]
}

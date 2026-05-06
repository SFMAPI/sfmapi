# sfmapi Helm chart

Kubernetes-native install of the [sfmapi](https://github.com/sfmapi/sfmapi)
web tier, with optional in-cluster GPU workers and bundled
Postgres/Redis subcharts.

## Quick install

```bash
# Resolve subcharts
helm dependency update deploy/helm/sfmapi

# Install with defaults (web + bundled postgres + redis, no GPU worker)
helm install sfmapi ./deploy/helm/sfmapi \
    --namespace sfmapi --create-namespace
```

## Production values

```yaml
# values-prod.yaml
image:
  tag: "v0.1.0"
env:
  authMode: api_key
web:
  replicas: 3
  ingress:
    enabled: true
    className: nginx
    hosts:
      - host: api.example.com
        paths: [{ path: /, pathType: Prefix }]
    tls:
      - hosts: [api.example.com]
        secretName: sfmapi-tls
  autoscaling:
    enabled: true
    maxReplicas: 12
worker:
  enabled: true
  image:
    repository: ghcr.io/your-org/sfmapi-worker
    tag: "v0.1.0-cuda12"
  nodeSelector:
    node.sfmapi/gpu: "true"
postgresql:
  enabled: false           # use a managed Postgres
env:
  extraEnv:
    SFMAPI_DB_URL: postgresql+psycopg://sfm:secret@db.svc.local:5432/sfmapi
```

```bash
helm upgrade --install sfmapi ./deploy/helm/sfmapi \
    -n sfmapi -f values-prod.yaml
```

## What gets created

| Resource | Always | When |
|---|---|---|
| `Deployment/<rel>-web` | ✓ | always |
| `Service/<rel>-web` | ✓ | always |
| `ServiceAccount` | ✓ | `serviceAccount.create=true` |
| `PersistentVolumeClaim/<rel>-workspaces` | ✓ | `workspace.persistentVolumeClaim.enabled=true` |
| `Ingress/<rel>-web` | | `web.ingress.enabled=true` |
| `HorizontalPodAutoscaler/<rel>-web` | | `web.autoscaling.enabled=true` |
| `DaemonSet/<rel>-worker` | | `worker.enabled=true` |
| `postgresql` (subchart) | ✓ | `postgresql.enabled=true` |
| `redis` (subchart) | ✓ | `redis.enabled=true` |

## GPU worker images

We deliberately do not publish a worker image: the wheel must be
built against your cluster's exact CUDA + cuDSS versions, which the
chart cannot pick for you. Build one off `colmap_mod` and reference
it via `worker.image.repository`. See
https://sfmapi.github.io/guides/deployment for a worker-image
Dockerfile template.

## Linting

```bash
helm lint deploy/helm/sfmapi
helm template release-name deploy/helm/sfmapi --debug | kubectl apply --dry-run=client -f -
```

## Workspace storage

The chart provisions a single PVC at `/workspaces` shared by every
web pod and (when enabled) every worker pod on every node. **Pick a
ReadWriteMany-capable StorageClass** (NFS, CephFS, EFS, Filestore).
The default `ReadWriteOnce` works for single-replica dev installs.

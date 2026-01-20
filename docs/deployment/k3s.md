# AI Interviewer - k3s Deployment Guide

This guide details how to deploy the AI Interviewer application on a k3s cluster, securing it with Cloudflare Tunnel (Tunnel).

## Prerequisites

1.  **k3s Cluster**: A running k3s cluster (single node or multi-node).
2.  **Cloudflare Tunnel**: `cloudflared` installed and authenticated on your k3s host or a gateway node.
3.  **Docker**: Ability to build images on a node that k3s can access (or use `k3s ctr` to import).

## 1. Build & Import Images

Since this is a homelab, you can build images locally and import them directly into k3s's containerd registry.

```bash
# Export images to tarballs
docker build -t ai-interviewer-backend:latest ./backend
docker save ai-interviewer-backend:latest -o backend.tar

docker build -t ai-interviewer-frontend:latest ./frontend
docker save ai-interviewer-frontend:latest -o frontend.tar

# Import into k3s
sudo k3s ctr images import backend.tar
sudo k3s ctr images import frontend.tar
```

*Verification*: Run `sudo k3s crictl images` to ensure the images are present.

## 2. Configure Secrets

Edit `k8s/02-secrets.yaml` and fill in your actual values:
*   `POSTGRES_PASSWORD`: Use a strong password.
*   `SECRET_KEY`: Generate with `openssl rand -hex 32`.
*   `OPENAI_API_KEY` / `GEMINI_API_KEY`: Your LLM keys.

## 2.5 Frontend Environment Configuration

In production, you must set the `VITE_API_URL` environment variable for the frontend if your API is hosted on a separate subdomain.

**CRITICAL:** The URL must end with `/api`.

*   **Scenario A**: Separate API Subdomain (e.g., `api.example.com`)
    *   Set `VITE_API_URL` to `https://api.example.com/api`
*   **Scenario B**: Common Domain (e.g., `example.com/api`)
    *   Leave `VITE_API_URL` empty (defaults to relative `/api` path)

You can set this in `k8s/05-frontend.yaml` as an environment variable or via a ConfigMap.

## 3. Apply Manifests

Apply the manifests in order:

```bash
kubectl apply -f k8s/01-namespace.yaml
kubectl apply -f k8s/02-secrets.yaml
kubectl apply -f k8s/03-postgres.yaml
# Wait for postgres to be running
kubectl apply -f k8s/04-backend.yaml
kubectl apply -f k8s/05-frontend.yaml
```

## 4. Setup Cloudflare Tunnel

Configure your `cloudflared` config.yml (usually in `/etc/cloudflared/config.yml` or mapped config) to point to your k3s Service Cluster IPs.

**Example `config.yml`:**

```yaml
tunnel: <Your-Tunnel-UUID>
credentials-file: /root/.cloudflared/<UUID>.json

ingress:
  # Backend API
  - hostname: api.ai-interviewer.yourdomain.com
    service: http://<BACKEND_CLUSTER_IP>:8000
  
  # Frontend
  - hostname: ai-interviewer.yourdomain.com
    service: http://<FRONTEND_CLUSTER_IP>:80
    
  - service: http_status:404
```

To find the Cluster IPs:
```bash
kubectl get svc -n ai-interviewer
# Look for CLUSTER-IP column for 'backend' and 'frontend' services
```

*Note: Alternatively, if you use a CNI that allows host routing or NodePort services, you can point to `localhost:<NodePort>`, but internal Service IP mapping is cleanest if `cloudflared` runs on the cluster as a pod or on the master node.*

## 5. Verification

1.  Visit `https://ai-interviewer.yourdomain.com`.
2.  Frontend should load.
3.  Try logging in (default admin credentials will be seeded if you ran migration logic, otherwise create a first user).

## Troubleshooting

*   **Database connection**: Check backend logs: `kubectl logs -l app=backend -n ai-interviewer`.
*   **Static files 404**: Check frontend nginx logs: `kubectl logs -l app=frontend -n ai-interviewer`.

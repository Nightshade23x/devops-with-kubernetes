# Log output

Generates a timestamp and UUID every 5 seconds.

Uses a ConfigMap and retrieves the Ping-pong counter through HTTP.

## GitOps

Install Argo CD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd --server-side --force-conflicts -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Register the application from the repository root:

```bash
kubectl apply -f log_output/argocd-application.yaml
```

GitHub Actions builds and publishes a new Docker image when application code changes and commits the updated image tag.

Argo CD automatically synchronizes changes from GitHub to GKE.

## Verification

```bash
kubectl get applications -n argocd
kubectl get pods -n exercises
kubectl logs deployment/log-output -n exercises -c log-writer
```

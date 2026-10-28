
# Todo App

A Python web server that uses the PORT environment variable (default 3000).

## Run

```bash
docker build -t todo-app:1.2 .
k3d image import todo-app:1.2 -c dwk
kubectl apply -f manifests/deployment.yaml
kubectl logs deployment/todo-app
```

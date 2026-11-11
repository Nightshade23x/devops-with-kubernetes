
# Todo App

Displays a cached random image, a todo input (max 140 characters), a Send button and a list of hardcoded todos.
Configuration is provided through Kubernetes environment variables.

## Run

```bash
kubectl apply -f ../storage/todo-pv.yaml
kubectl apply -f ../storage/todo-pvc.yaml
docker build -t todo-app:1.12 .
k3d image import todo-app:1.12 -c dwk
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
kubectl apply -f ../log_output/manifests/ingress.yaml
```

Open http://localhost:8081/todo

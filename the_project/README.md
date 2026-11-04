
# Todo App

Displays a random image from Lorem Picsum.

Images are cached for 10 minutes using persistent storage.

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

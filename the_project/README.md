
# Todo App

A Python web server that uses the PORT environment variable (default 3000).

## Run

```bash
docker build -t todo-app:1.2 .
k3d image import todo-app:1.2 -c dwk
kubectl apply -f manifests/deployment.yaml
kubectl logs deployment/todo-app
```


## Access

```bash
kubectl port-forward deployment/todo-app 8080:3000
```

Open http://localhost:8080/

## NodePort

```bash
kubectl apply -f manifests/service.yaml
k3d cluster edit dwk --port-add "30080:30080@server:0"
```

Open http://localhost:30080/

# Todo App

Python web server using port 3000 by default. The PORT enviroment variable can change the port.

## Run

```bash
docker build -t todo-app:1.2 .
k3d image import todo-app:1.2 -c dwk
kubectl apply -f manifests/
```

Access through Ingress at http://localhost:8081/

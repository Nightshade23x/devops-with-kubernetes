
# Log output

Generates a random UUID at startup and prints it with a timestampp every 5 seconds. The current status is available through an HTTP endpoint.

## Run

```bash
docker build -t log-output:1.7 .
k3d image import log-output:1.7 -c dwk
kubectl apply -f manifests/
kubectl logs deployment/log-output
```

## Access

```bash
k3d cluster edit dwk --port-add "8081:80@loadbalancer"
```

Open http://localhost:8081/

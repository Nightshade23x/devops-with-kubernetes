
# Log output

Generates a timestamp and UUID every 5 seconds.

Uses a ConfigMap for a file and environment variable. Gets the Ping-pong counter through HTTP.

## Run

```bash
docker build -t log-output:2.5 .
k3d image import log-output:2.5 -c dwk
kubectl apply -f manifests/
```

Open http://localhost:8081/

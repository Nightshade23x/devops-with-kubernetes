
# Log output

Writes a timestamp and UUID to a shared file every 5 seconds.

The reader container serves the status and Ping-pong counter through HTTP.

## Run

```bash
docker build -t log-output:1.11 .
k3d image import log-output:1.11 -c dwk
kubectl apply -f manifests/
```

Access at http://localhost:8081/

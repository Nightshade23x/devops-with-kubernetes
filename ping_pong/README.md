
# Ping-pong

Returns an increasing counter at /pingpong and saves it to a persistent volume.

## Run

```bash
docker build -t ping-pong:1.11 .
k3d image import ping-pong:1.11 -c dwk
kubectl apply -f manifests/
```

Access at http://localhost:8081/pingpong

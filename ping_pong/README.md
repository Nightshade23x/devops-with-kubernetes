
# Ping-pong

Stores the request counter in PostgreSQL.

- GET /pingpong increments the counter.
- GET /pings returns the current count.

## Run

```bash
docker build -t ping-pong:2.7 .
k3d image import ping-pong:2.7 -c dwk
kubectl apply -f manifests/
```

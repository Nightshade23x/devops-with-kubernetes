
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

## GKE

Deployed Ping-pong to Google Kubernetes Engine using a LoadBalancer Service and PostgreSQL.

GKE configurations are in `gke-deployment.yaml` and `gke-service.yaml`.

## GKE Ingress

Ping-pong is exposed at `/pingpong` through GKE Ingress.
The `/` endpoint returns HTTP 200 for health checks.

## Gateway API

Ping-pong is exposed at `/pingpong` using GKE Gateway API.
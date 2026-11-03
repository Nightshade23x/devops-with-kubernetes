
# Log output

Writes a timestamp and UUID to a shared file every 5 seconds.

Two containers run in the same Pod:
- Log writer writes to the file.
- Log reader serves the file through HTTP.

## Run

```bash
docker build -t log-output:1.10 .
k3d image import log-output:1.10 -c dwk
kubectl apply -f manifests/
```

## Check

```bash
kubectl get pods
kubectl logs deployment/log-output -c log-writer
```

Access at http://localhost:8081/

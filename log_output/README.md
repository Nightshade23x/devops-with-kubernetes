# Log output

Generates a random UUID at startup and prints it with a timestamp every 5 seconds.

## Run

With Docker running, create the cluster if it doesn't exist:

`k3d cluster create dwk`

From the `log_output` directory, run:

```bash
docker build -t log-output:1.1 .
k3d image import log-output:1.1 -c dwk
kubectl apply -f manifests/deployment.yaml
```

Check the logs:

```bash
kubectl logs deployment/log-output
```
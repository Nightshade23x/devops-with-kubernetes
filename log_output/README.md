# Log Output Application

DevOps with Kubernetes — Exercise 1.1

## Description

A Python application that generates a random UUID at startup,
stores it in memory, and prints the current UTC timestamp
alongside the UUID every 5 seconds.

The application is containerized using Docker and deployed
to a local Kubernetes cluster using k3d.

## Requirements

- Python 3
- Docker
- kubectl
- k3d

## Running Locally

```bash
python app.py
```

## Running with Docker

Build the image:

```bash
docker build -t log-output:1.1 .
```

Run the container:

```bash
docker run --rm log-output:1.1
```

## Deploying to Kubernetes

Create a cluster if one does not already exist:

```bash
k3d cluster create dwk
```

Import the Docker image:

```bash
k3d image import log-output:1.1 -c dwk
```

Apply the Deployment:

```bash
kubectl apply -f manifests/deployment.yaml
```

Verify that the application is running:

```bash
kubectl get pods
```

View the application logs:

```bash
kubectl logs deployment/log-output
```

## Expected Output

The application outputs a timestamp and the same UUID every
5 seconds. The UUID only changes when the application restarts.
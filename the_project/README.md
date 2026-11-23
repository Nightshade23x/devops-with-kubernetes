
# Todo App

Displays a cached random image, a todo input (max 140 characters), a Send button and a list of hardcoded todos.
Configuration is provided through Kubernetes environment variables.

## Run

```bash
kubectl apply -f ../storage/todo-pv.yaml
kubectl apply -f ../storage/todo-pvc.yaml
docker build -t todo-app:1.12 .
k3d image import todo-app:1.12 -c dwk
kubectl apply -f manifests/deployment.yaml
kubectl apply -f manifests/service.yaml
kubectl apply -f ../log_output/manifests/ingress.yaml
```

Open http://localhost:8081/todo

Automatic GKE deployment is configured using GitHub Actions and Kustomize.


## 3.9 — DBaaS vs DIY
### DBaaS

**Pros:**
- Easy to set up, with very little configration required.
- Automatic backups and easier database recovery.
- Provider handles the updates, maintenance and much of the scaling.

**Cons:**
- Generally higher infrastructure costs.
- Less control over the database infrastructure.
- Dependence on the cloud provider.

### DIY (PostgreSQL in Kubernetes)

**Pros:**
- More control over database configuration and deployment.
- Can be cheaper for small workloads when using existing infrastructure.
- Easier to customize and move between environments.

**Cons:**
- More initial setup work, including storage and networking.
- Responsible for updates, monitoring, security and recovery.
- Backups must be configured and managed manually, using tools such as `pg_dump`. Restores must also be tested.

### Conclusion

DBaaS is preferable for production applications where reliability and reduced maintenance are important. DIY is suitable for learning and smaller projects where control and potentially lower infrastructure costs matter more.

## Database backups

A Kubernetes CronJob backs up the Todo PostgreSQL database daily at 02:00 UTC using `pg_dump`.

Backups are uploaded to a private Google Cloud Storage bucket using Workload Identity Federation for GKE.

The backup resources are defined in `gke_project/`.
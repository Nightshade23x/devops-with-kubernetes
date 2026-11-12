
# Todo PostgreSQL

PostgreSQL StatefulSet with persistent storage for the Todo application.

## Run

Create a Secret named `todo-db-secret` in the `project` namespace with the key `POSTGRES_PASSWORD`.

```bash
kubectl apply -f manifests/
```

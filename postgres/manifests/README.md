
# PostgreSQL

PostgreSQL StatefulSet with persistent storage.

## Run

Create the database password Secret:

```powershell
kubectl create secret generic ping-pong-db-secret -n exercises --from-literal=POSTGRES_PASSWORD=YOUR_PASSWORD
```

Deploy:

```powershell
kubectl apply -f manifests/
```

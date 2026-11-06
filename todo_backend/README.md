
# Todo Backend

Stores todos in memory.

- GET /todos — returns all todos.
- POST /todos — adds a new todo (maximum 140 characters).

## Run

```bash
docker build -t todo-backend:2.2 .
k3d image import todo-backend:2.2 -c dwk
kubectl apply -f manifests/
```

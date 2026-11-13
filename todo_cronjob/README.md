
# Wikipedia Reminder CronJob

Creates a todo every hour containing a random Wikipedia article URL.

## Run

```bash
docker build -t todo-cronjob:2.9 .
k3d image import todo-cronjob:2.9 -c dwk
kubectl apply -f manifests/
```

## Test

```bash
kubectl create job wikipedia-reminder-test --from=cronjob/wikipedia-reminder -n project
kubectl logs job/wikipedia-reminder-test -n project
```

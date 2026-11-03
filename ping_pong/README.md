# Ping-pong

Returns an increasing counter at /pingpong.

## Run

Build and deploy:

docker build -t ping-pong:1.9 .
k3d image import ping-pong:1.9 -c dwk
kubectl apply -f manifests/
kubectl apply -f ../log_output/manifests/

Access at http://localhost:8081/pingpong
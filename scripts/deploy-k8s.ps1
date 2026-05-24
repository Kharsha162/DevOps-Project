# Deploy full platform to Kubernetes
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host "=== Deploying E-Commerce Platform to Kubernetes ===" -ForegroundColor Cyan

kubectl apply -f "$root/kubernetes/namespace.yaml"
kubectl apply -f "$root/kubernetes/secrets/"
kubectl apply -f "$root/kubernetes/configmaps/"
kubectl apply -f "$root/kubernetes/storage/"
kubectl apply -f "$root/kubernetes/deployments/postgres-deployment.yaml"
kubectl apply -f "$root/kubernetes/deployments/redis-deployment.yaml"
kubectl apply -f "$root/kubernetes/deployments/kafka-deployment.yaml"
kubectl apply -f "$root/kubernetes/services/postgres-service.yaml"
kubectl apply -f "$root/kubernetes/services/redis-service.yaml"
kubectl apply -f "$root/kubernetes/deployments/"
kubectl apply -f "$root/kubernetes/services/"
kubectl apply -f "$root/kubernetes/monitoring/"
kubectl apply -f "$root/kubernetes/hpa/"
kubectl apply -f "$root/kubernetes/ingress/"

Write-Host "Waiting for api-gateway rollout..." -ForegroundColor Yellow
kubectl rollout status deployment/api-gateway -n ecommerce --timeout=180s

Write-Host "=== Pod Status ===" -ForegroundColor Green
kubectl get pods -n ecommerce

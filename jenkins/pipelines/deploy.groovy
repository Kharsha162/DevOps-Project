#!/usr/bin/env groovy
def call(String namespace = 'ecommerce') {
    echo "Deploying to Kubernetes namespace: ${namespace}"
    sh """
        kubectl apply -f kubernetes/namespace.yaml
        kubectl apply -f kubernetes/secrets/
        kubectl apply -f kubernetes/configmaps/
        kubectl apply -f kubernetes/storage/
        kubectl apply -f kubernetes/deployments/
        kubectl apply -f kubernetes/services/
        kubectl apply -f kubernetes/monitoring/
        kubectl apply -f kubernetes/hpa/
        kubectl apply -f kubernetes/ingress/
        kubectl rollout status deployment/api-gateway -n ${namespace} --timeout=180s
    """
}

def rollback(String namespace = 'ecommerce') {
    echo "Rolling back deployments in ${namespace}"
    sh """
        kubectl rollout undo deployment/api-gateway -n ${namespace} || true
        kubectl rollout undo deployment/auth-service -n ${namespace} || true
        kubectl rollout undo deployment/product-service -n ${namespace} || true
        kubectl rollout undo deployment/cart-service -n ${namespace} || true
    """
}

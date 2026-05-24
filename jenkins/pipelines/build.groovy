#!/usr/bin/env groovy
def call(String buildTag = 'latest') {
    echo "Building Docker images with tag: ${buildTag}"
    sh """
        docker build -t mycommerce/api-gateway:${buildTag} api-gateway
        docker build -t mycommerce/frontend:${buildTag} frontend
        docker build -t mycommerce/auth-service:${buildTag} services/auth
        docker build -t mycommerce/product-service:${buildTag} services/product
        docker build -t mycommerce/cart-service:${buildTag} services/cart
        docker build -t mycommerce/order-service:${buildTag} services/order
        docker build -t mycommerce/payment-service:${buildTag} services/payment
        docker build -t mycommerce/notification-service:${buildTag} services/notification
    """
}

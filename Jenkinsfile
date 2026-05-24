pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'mycommerce'
        BUILD_TAG = "${env.BUILD_NUMBER ?: 'latest'}"
        K8S_NAMESPACE = 'ecommerce'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test Services') {
            parallel {
                stage('Test Auth') {
                    steps {
                        dir('services/auth') {
                            sh 'pip install -q -r requirements.txt PyJWT==2.8.0'
                            sh 'python -c "from app import create_app; create_app()"'
                        }
                    }
                }
                stage('Test Product') {
                    steps {
                        dir('services/product') {
                            sh 'pip install -q -r requirements.txt'
                            sh 'python -c "from app import create_app; create_app()"'
                        }
                    }
                }
                stage('Test Cart') {
                    steps {
                        dir('services/cart') {
                            sh 'pip install -q -r requirements.txt'
                            sh 'python -c "from app import create_app; create_app()"'
                        }
                    }
                }
                stage('Test Gateway') {
                    steps {
                        dir('api-gateway') {
                            sh 'pip install -q -r requirements.txt'
                            sh 'python -c "from app import create_app; create_app()"'
                        }
                    }
                }
                stage('Test Frontend') {
                    steps {
                        dir('frontend') {
                            sh 'npm ci || npm install'
                            sh 'npm run build'
                        }
                    }
                }
            }
        }

        stage('Docker Build') {
            steps {
                script {
                    def services = [
                        'api-gateway',
                        'frontend',
                        'auth:auth-service',
                        'product:product-service',
                        'cart:cart-service',
                        'order:order-service',
                        'payment:payment-service',
                        'notification:notification-service'
                    ]
                    services.each { entry ->
                        def parts = entry.split(':')
                        def dir = parts[0] == 'api-gateway' ? 'api-gateway' : (parts[0] == 'frontend' ? 'frontend' : "services/${parts[0]}")
                        def image = parts.size() > 1 ? parts[1] : parts[0]
                        sh "docker build -t ${DOCKER_REGISTRY}/${image}:${BUILD_TAG} ${dir}"
                        sh "docker tag ${DOCKER_REGISTRY}/${image}:${BUILD_TAG} ${DOCKER_REGISTRY}/${image}:latest"
                    }
                }
            }
        }

        stage('Deploy Kubernetes') {
            steps {
                sh '''
                    kubectl apply -f kubernetes/namespace.yaml
                    kubectl apply -f kubernetes/secrets/
                    kubectl apply -f kubernetes/configmaps/
                    kubectl apply -f kubernetes/storage/
                    kubectl apply -f kubernetes/deployments/postgres-deployment.yaml
                    kubectl apply -f kubernetes/deployments/redis-deployment.yaml
                    kubectl apply -f kubernetes/deployments/kafka-deployment.yaml
                    kubectl apply -f kubernetes/services/postgres-service.yaml
                    kubectl apply -f kubernetes/services/redis-service.yaml
                    kubectl apply -f kubernetes/deployments/
                    kubectl apply -f kubernetes/services/
                    kubectl apply -f kubernetes/monitoring/
                    kubectl apply -f kubernetes/hpa/
                    kubectl apply -f kubernetes/ingress/
                '''
            }
        }

        stage('Verify Deployment') {
            steps {
                sh 'kubectl rollout status deployment/api-gateway -n ecommerce --timeout=120s || true'
                sh 'kubectl get pods -n ecommerce'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed — rolling back api-gateway deployment...'
            sh 'kubectl rollout undo deployment/api-gateway -n ecommerce || true'
        }
    }
}

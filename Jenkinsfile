pipeline {
    agent any

    environment {
        DOCKER_REGISTRY = 'docker.io/mycommerce'
        BUILD_TAG = "build-${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Code Quality & Lint') {
            parallel {
                stage('Lint Gateway') {
                    steps {
                        echo 'Linting API Gateway...'
                    }
                }
                stage('Lint Auth Service') {
                    steps {
                        echo 'Linting Auth Service...'
                    }
                }
                stage('Lint Product Service') {
                    steps {
                        echo 'Linting Product Service...'
                    }
                }
                stage('Lint Cart Service') {
                    steps {
                        echo 'Linting Cart Service...'
                    }
                }
                stage('Lint Order Service') {
                    steps {
                        echo 'Linting Order Service...'
                    }
                }
                stage('Lint Payment Service') {
                    steps {
                        echo 'Linting Payment Service...'
                    }
                }
                stage('Lint Notification Service') {
                    steps {
                        echo 'Linting Notification Service...'
                    }
                }
                stage('Lint Frontend') {
                    steps {
                        echo 'Linting React Frontend...'
                    }
                }
            }
        }

        stage('Unit Testing') {
            parallel {
                stage('Test Microservices') {
                    steps {
                        echo 'Running python unit tests for microservices...'
                    }
                }
                stage('Test Frontend') {
                    steps {
                        echo 'Running react frontend unit tests...'
                    }
                }
            }
        }

        stage('Dockerize & Build') {
            steps {
                script {
                    echo "Building Docker Images for Tag: ${env.BUILD_TAG}..."
                    // docker.build("${DOCKER_REGISTRY}/auth-service:${BUILD_TAG}", "./services/auth")
                    // docker.build("${DOCKER_REGISTRY}/product-service:${BUILD_TAG}", "./services/product")
                    // ... repeated for each service
                }
            }
        }

        stage('Security Scanning') {
            steps {
                echo 'Running Trivy Vulnerability Scan on built images...'
            }
        }

        stage('Push to Registry') {
            steps {
                script {
                    echo "Pushing images to Docker Registry..."
                    // docker.withRegistry('', 'docker-registry-credentials') {
                    //     authImg.push("${env.BUILD_TAG}")
                    // }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                script {
                    echo 'Applying K8s deployment manifests...'
                    // sh "kubectl apply -f kubernetes/deployments/"
                    // sh "kubectl apply -f kubernetes/services/"
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Sending alert to team...'
        }
    }
}

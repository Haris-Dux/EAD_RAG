pipeline {
    agent any

    environment {
        DOCKER_BUILDKIT = '1'
        APP_NAME = 'ead_rag'
        VPS_IP = '145.79.10.245'
    }

    stages {
        stage('Set Environment') {
            steps {
                script {
                    echo 'Setting Environment'
                    def branchName = env.GIT_BRANCH?.replace('origin/', '')
                    echo "Branch name is: ${branchName}"
                    if (branchName == 'main') {
                        echo "Branch name: ${branchName}"
                        env.ENVIRONMENT = 'prod'
                        env.PORT = 8000
                    } else {
                        error "Unrecognized branch: ${env.BRANCH_NAME}. Only 'main' is supported."
                    }
                    echo "Building for ${env.ENVIRONMENT} environment."
                    env.DOCKER_IMAGE_RAG = "${APP_NAME}:backend-${env.ENVIRONMENT}-${BUILD_NUMBER}"
                    echo "Rag application image to be configured: ${env.DOCKER_IMAGE_RAG}"
                }
            }
        }

        stage('Verify Prerequisites') {
            steps {
                script {
                    sh '''

                        # Ensure Docker daemon is running
                        if ! docker info >/dev/null 2>&1; then
                            echo "Docker daemon is not running. Please start Docker service."
                            exit 1
                        fi

                        # Display versions for logging
                        echo "Docker version:"
                        docker --version

                    '''
                }
            }
        }

        stage('Docker Build & Deploy') {
            steps {
                script {
                    sh """

                        echo "Building rag application image"
                            docker build -t ${env.DOCKER_IMAGE_RAG} -f Dockerfile .

                """
                }
            }
        }

        stage('Deploy to VPS') {
            steps {
                script {
                    sh """

                        echo "Stopping old container"
                        docker stop ead-rag-${env.ENVIRONMENT} || true
                        docker rm ead-rag-${env.ENVIRONMENT} || true

                        echo "Running new container"
                        sudo docker run -d --name ead-rag-${env.ENVIRONMENT} -p ${env.PORT}:8000 ${env.DOCKER_IMAGE_RAG}

                        echo "Restarting Nginx"
                        sudo systemctl restart nginx

                """
                }
            }
        }
    }

    post {
        always {
            // Clean workspace
            cleanWs()
        }
        success {
            script {
                sh '''
                    echo "Deployment successful!"
                '''
            }
        }
        failure {
            script {
                sh '''
                    echo "Deployment failed!"
                '''
            }
        }
    }
}

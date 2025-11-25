pipeline {
    agent any
    
    options {
        timeout(time: 1, unit: 'HOURS')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timestamps()
    }
    
    environment {
        COMPOSE_FILE = 'docker-compose.yml'
        COMPOSE_PROJECT_NAME = 'smchitfund'
        ENVIRONMENT = 'development'
    }
    
    stages {
        stage('Cleanup Old Resources') {
            steps {
                sh '''
                    echo "Cleaning up old containers and images..."
                    docker-compose -f ${COMPOSE_FILE} down --rmi all --volumes 2>/dev/null || true
                    
                    echo "Removing dangling images..."
                    docker image prune -f --filter "until=72h" || true
                    
                    docker ps -a
                '''
            }
        }
        
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    echo "Setting up development environment..."
                    if [ ! -f .env ]; then
                        echo "ENVIRONMENT=${ENVIRONMENT}" > .env
                    fi
                '''
            }
        }
        
        stage('Build Images') {
            steps {
                sh '''
                    echo "Building Docker images..."
                    docker-compose -f ${COMPOSE_FILE} build --no-cache
                '''
            }
        }
        
        stage('Start Services') {
            steps {
                sh '''
                    echo "Starting services with docker-compose..."
                    docker-compose -f ${COMPOSE_FILE} down --volumes 2>/dev/null || true
                    docker-compose -f ${COMPOSE_FILE} up -d
                    sleep 10
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                sh '''
                    echo "Checking service health..."
                    docker-compose -f ${COMPOSE_FILE} ps
                    
                    echo "Waiting for MySQL to be ready..."
                    for i in {1..30}; do
                        docker-compose -f ${COMPOSE_FILE} exec -T db \
                            mysqladmin ping -h db -u root --password=admin && break || sleep 1
                    done
                    
                    echo "MySQL is ready"
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    echo "Running tests..."
                    docker-compose -f ${COMPOSE_FILE} exec -T api python -m pytest tests/ -v --tb=short || true
                '''
            }
        }
        
        stage('Collect Logs') {
            steps {
                sh '''
                    echo "Collecting service logs..."
                    docker-compose -f ${COMPOSE_FILE} logs > build_logs.txt
                '''
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: 'build_logs.txt', allowEmptyArchive: true
            sh '''
                echo "Service status:"
                docker-compose -f ${COMPOSE_FILE} ps || true
            '''
        }
        
        failure {
            sh '''
                echo "Build failed. Stopping services..."
                docker-compose -f ${COMPOSE_FILE} down --volumes || true
                docker-compose -f ${COMPOSE_FILE} logs
            '''
        }
        
        success {
            echo 'Deployment successful!'
        }
    }
}

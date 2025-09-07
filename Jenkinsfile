pipeline {
    agent any
    
    environment {
        // Python version
        PYTHON_VERSION = '3.11'
        
        // Application settings
        APP_NAME = 'smchitfund-python-api'
        APP_PORT = '8000'
        
        // Docker settings
        DOCKER_IMAGE = "${APP_NAME}"
        DOCKER_TAG = "${BUILD_NUMBER}"
        DOCKER_REGISTRY = 'your-docker-registry.com' // Update with your registry
        
        // Database settings (for testing)
        DB_HOST = 'localhost'
        DB_PORT = '3306'
        DB_NAME = 'test_smchitfund'
        DB_USER = 'test_user'
        DB_PASSWORD = credentials('db-password') // Store in Jenkins credentials
        
        // SonarQube settings
        SONAR_PROJECT_KEY = 'smchitfund-python-api'
        SONAR_PROJECT_NAME = 'SM ChitFund Python API'
        
        // Deployment settings
        STAGING_SERVER = 'staging.smchitfund.com'
        PRODUCTION_SERVER = 'api.smchitfund.com'
    }
    
    tools {
        // Ensure Python is available
        python 'Python-3.11'
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code...'
                checkout scm
                
                // Display build information
                script {
                    echo "Building ${APP_NAME} - Build #${BUILD_NUMBER}"
                    echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                    echo "Commit: ${env.GIT_COMMIT}"
                }
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo 'Setting up Python environment...'
                sh '''
                    # Create virtual environment
                    python3 -m venv venv
                    
                    # Activate virtual environment and install dependencies
                    . venv/bin/activate
                    
                    # Upgrade pip
                    pip install --upgrade pip
                    
                    # Install dependencies
                    pip install -r requirements.txt
                    
                    # Install development dependencies
                    pip install pytest pytest-cov pytest-asyncio httpx flake8 black isort mypy bandit safety
                    
                    # Display installed packages
                    pip list
                '''
            }
        }
        
        stage('Code Quality Analysis') {
            parallel {
                stage('Linting with Flake8') {
                    steps {
                        echo 'Running Flake8 linting...'
                        sh '''
                            . venv/bin/activate
                            flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                            flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
                        '''
                    }
                }
                
                stage('Code Formatting Check') {
                    steps {
                        echo 'Checking code formatting with Black...'
                        sh '''
                            . venv/bin/activate
                            black --check --diff .
                        '''
                    }
                }
                
                stage('Import Sorting Check') {
                    steps {
                        echo 'Checking import sorting with isort...'
                        sh '''
                            . venv/bin/activate
                            isort --check-only --diff .
                        '''
                    }
                }
                
                stage('Type Checking') {
                    steps {
                        echo 'Running type checking with MyPy...'
                        sh '''
                            . venv/bin/activate
                            mypy . --ignore-missing-imports || true
                        '''
                    }
                }
            }
        }
        
        stage('Security Analysis') {
            parallel {
                stage('Security Scan with Bandit') {
                    steps {
                        echo 'Running security analysis with Bandit...'
                        sh '''
                            . venv/bin/activate
                            bandit -r . -f json -o bandit-report.json || true
                            bandit -r . || true
                        '''
                        
                        // Archive security report
                        archiveArtifacts artifacts: 'bandit-report.json', allowEmptyArchive: true
                    }
                }
                
                stage('Dependency Security Check') {
                    steps {
                        echo 'Checking dependencies for security vulnerabilities...'
                        sh '''
                            . venv/bin/activate
                            safety check --json --output safety-report.json || true
                            safety check || true
                        '''
                        
                        // Archive safety report
                        archiveArtifacts artifacts: 'safety-report.json', allowEmptyArchive: true
                    }
                }
            }
        }
        
        stage('Unit Tests') {
            steps {
                echo 'Running unit tests...'
                sh '''
                    . venv/bin/activate
                    
                    # Run tests with coverage
                    pytest test_*.py -v --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing --junitxml=test-results.xml
                '''
                
                // Publish test results
                publishTestResults testResultsPattern: 'test-results.xml'
                
                // Publish coverage report
                publishCoverage adapters: [coberturaAdapter('coverage.xml')], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                
                // Archive coverage report
                archiveArtifacts artifacts: 'htmlcov/**', allowEmptyArchive: true
            }
        }
        
        stage('Integration Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    changeRequest()
                }
            }
            steps {
                echo 'Running integration tests...'
                script {
                    // Start test database if needed
                    sh '''
                        . venv/bin/activate
                        
                        # Set test environment variables
                        export TESTING=true
                        export DATABASE_URL="mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"
                        
                        # Run integration tests
                        pytest test_api.py test_interest.py -v --junitxml=integration-test-results.xml
                    '''
                }
                
                // Publish integration test results
                publishTestResults testResultsPattern: 'integration-test-results.xml'
            }
        }
        
        stage('SonarQube Analysis') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                script {
                    def scannerHome = tool 'SonarQubeScanner'
                    withSonarQubeEnv('SonarQube') {
                        sh """
                            ${scannerHome}/bin/sonar-scanner \\
                                -Dsonar.projectKey=${SONAR_PROJECT_KEY} \\
                                -Dsonar.projectName='${SONAR_PROJECT_NAME}' \\
                                -Dsonar.sources=. \\
                                -Dsonar.tests=. \\
                                -Dsonar.test.inclusions=test_*.py \\
                                -Dsonar.python.version=3 \\
                                -Dsonar.sourceEncoding=UTF-8 \\
                                -Dsonar.exclusions='**/tests/**,**/*.pyc,**/__pycache__/**,venv/**,htmlcov/**' \\
                                -Dsonar.python.coverage.reportPaths=coverage.xml \\
                                -Dsonar.python.xunit.reportPath=test-results.xml
                        """
                    }
                }
            }
        }
        
        stage('Quality Gate') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    changeRequest()
                }
            }
            steps {
                echo 'Building Docker image...'
                script {
                    // Update Dockerfile to use correct entrypoint
                    sh '''
                        # Create optimized Dockerfile for production
                        cat > Dockerfile.prod << 'EOF'
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    default-libmysqlclient-dev \\
    pkg-config \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \\
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \\
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/ || exit 1

# Run the application
CMD ["python", "main.py"]
EOF
                    '''
                    
                    // Build Docker image
                    def image = docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}", "-f Dockerfile.prod .")
                    
                    // Tag as latest for main branch
                    if (env.BRANCH_NAME == 'main') {
                        image.tag('latest')
                    }
                    
                    // Store image for later use
                    env.DOCKER_IMAGE_FULL = "${DOCKER_IMAGE}:${DOCKER_TAG}"
                }
            }
        }
        
        stage('Security Scan Docker Image') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo 'Scanning Docker image for vulnerabilities...'
                script {
                    // Using Trivy for container scanning (install Trivy on Jenkins agent)
                    sh """
                        # Scan Docker image with Trivy
                        trivy image --format json --output trivy-report.json ${DOCKER_IMAGE_FULL} || true
                        trivy image ${DOCKER_IMAGE_FULL} || true
                    """
                    
                    // Archive security scan report
                    archiveArtifacts artifacts: 'trivy-report.json', allowEmptyArchive: true
                }
            }
        }
        
        stage('Push to Registry') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    docker.withRegistry("https://${DOCKER_REGISTRY}", 'docker-registry-credentials') {
                        def image = docker.image("${DOCKER_IMAGE_FULL}")
                        image.push()
                        
                        if (env.BRANCH_NAME == 'main') {
                            image.push('latest')
                        }
                    }
                }
            }
        }
        
        stage('Deploy to Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Deploying to staging environment...'
                script {
                    // Deploy to staging server
                    sh """
                        # Deploy using docker-compose or kubernetes
                        ssh -o StrictHostKeyChecking=no deploy@${STAGING_SERVER} '
                            docker pull ${DOCKER_REGISTRY}/${DOCKER_IMAGE_FULL}
                            docker stop ${APP_NAME}-staging || true
                            docker rm ${APP_NAME}-staging || true
                            docker run -d \\
                                --name ${APP_NAME}-staging \\
                                -p ${APP_PORT}:8000 \\
                                -e DATABASE_URL=\$STAGING_DATABASE_URL \\
                                -e ENVIRONMENT=staging \\
                                --restart unless-stopped \\
                                ${DOCKER_REGISTRY}/${DOCKER_IMAGE_FULL}
                        '
                    """
                }
            }
        }
        
        stage('Smoke Tests - Staging') {
            when {
                branch 'develop'
            }
            steps {
                echo 'Running smoke tests on staging...'
                sh '''
                    . venv/bin/activate
                    
                    # Wait for application to start
                    sleep 30
                    
                    # Run smoke tests
                    python -c "
import requests
import sys

try:
    # Test health endpoint
    response = requests.get('http://${STAGING_SERVER}:${APP_PORT}/api/')
    assert response.status_code == 200
    print('✓ Health check passed')
    
    # Test API documentation
    response = requests.get('http://${STAGING_SERVER}:${APP_PORT}/docs')
    assert response.status_code == 200
    print('✓ API documentation accessible')
    
    print('All smoke tests passed!')
except Exception as e:
    print(f'✗ Smoke test failed: {e}')
    sys.exit(1)
"
                '''
            }
        }
        
        stage('Deploy to Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to production environment...'
                input message: 'Deploy to production?', ok: 'Deploy'
                
                script {
                    // Deploy to production server
                    sh """
                        # Deploy using docker-compose or kubernetes
                        ssh -o StrictHostKeyChecking=no deploy@${PRODUCTION_SERVER} '
                            docker pull ${DOCKER_REGISTRY}/${DOCKER_IMAGE_FULL}
                            docker stop ${APP_NAME}-prod || true
                            docker rm ${APP_NAME}-prod || true
                            docker run -d \\
                                --name ${APP_NAME}-prod \\
                                -p ${APP_PORT}:8000 \\
                                -e DATABASE_URL=\$PRODUCTION_DATABASE_URL \\
                                -e ENVIRONMENT=production \\
                                --restart unless-stopped \\
                                ${DOCKER_REGISTRY}/${DOCKER_IMAGE_FULL}
                        '
                    """
                }
            }
        }
        
        stage('Smoke Tests - Production') {
            when {
                branch 'main'
            }
            steps {
                echo 'Running smoke tests on production...'
                sh '''
                    . venv/bin/activate
                    
                    # Wait for application to start
                    sleep 30
                    
                    # Run smoke tests
                    python -c "
import requests
import sys

try:
    # Test health endpoint
    response = requests.get('https://${PRODUCTION_SERVER}/api/')
    assert response.status_code == 200
    print('✓ Production health check passed')
    
    print('Production deployment successful!')
except Exception as e:
    print(f'✗ Production smoke test failed: {e}')
    sys.exit(1)
"
                '''
            }
        }
    }
    
    post {
        always {
            echo 'Cleaning up...'
            
            // Clean up workspace
            sh '''
                # Remove virtual environment
                rm -rf venv
                
                # Clean up Docker images (keep last 3 builds)
                docker image prune -f
            '''
            
            // Archive artifacts
            archiveArtifacts artifacts: '**/*.log', allowEmptyArchive: true
        }
        
        success {
            echo 'Pipeline completed successfully!'
            
            // Send success notification
            script {
                if (env.BRANCH_NAME == 'main') {
                    slackSend(
                        channel: '#deployments',
                        color: 'good',
                        message: "✅ ${APP_NAME} successfully deployed to production! Build: ${BUILD_NUMBER}"
                    )
                }
            }
        }
        
        failure {
            echo 'Pipeline failed!'
            
            // Send failure notification
            slackSend(
                channel: '#alerts',
                color: 'danger',
                message: "❌ ${APP_NAME} pipeline failed! Build: ${BUILD_NUMBER} Branch: ${env.BRANCH_NAME ?: 'main'}"
            )
        }
        
        unstable {
            echo 'Pipeline completed with warnings!'
            
            // Send warning notification
            slackSend(
                channel: '#alerts',
                color: 'warning',
                message: "⚠️ ${APP_NAME} pipeline completed with warnings! Build: ${BUILD_NUMBER}"
            )
        }
    }
}
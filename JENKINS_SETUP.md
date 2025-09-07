# Jenkins Pipeline Setup for SM ChitFund Python API

This document provides comprehensive instructions for setting up the Jenkins CI/CD pipeline for the SM ChitFund Python FastAPI application.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Jenkins Configuration](#jenkins-configuration)
3. [Pipeline Features](#pipeline-features)
4. [Environment Setup](#environment-setup)
5. [Security Configuration](#security-configuration)
6. [Deployment Configuration](#deployment-configuration)
7. [Monitoring and Notifications](#monitoring-and-notifications)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### Jenkins Server Requirements

- Jenkins 2.400+ with Blue Ocean plugin
- Docker installed on Jenkins agents
- Python 3.11+ available on Jenkins agents
- Git configured for repository access

### Required Jenkins Plugins

Install the following plugins in Jenkins:

```bash
# Core plugins
- Pipeline
- Blue Ocean
- Git
- Docker Pipeline
- Credentials Binding

# Testing and Quality
- JUnit
- Coverage
- SonarQube Scanner
- HTML Publisher

# Notifications
- Slack Notification
- Email Extension

# Security
- OWASP Dependency Check
- Anchore Container Image Scanner (optional)
```

### External Tools

1. **SonarQube Server** (for code quality analysis)
2. **Docker Registry** (for image storage)
3. **MySQL Database** (for testing)
4. **Slack Workspace** (for notifications)

## Jenkins Configuration

### 1. Global Tool Configuration

Navigate to `Manage Jenkins > Global Tool Configuration`:

#### Python Configuration
```
Name: Python-3.11
Installation: Install automatically
Version: Python 3.11.x
```

#### SonarQube Scanner
```
Name: SonarQubeScanner
Installation: Install automatically
Version: Latest
```

#### Docker
```
Name: docker
Installation: Install automatically
Version: Latest
```

### 2. System Configuration

Navigate to `Manage Jenkins > Configure System`:

#### SonarQube Servers
```
Name: SonarQube
Server URL: http://your-sonarqube-server:9000
Server authentication token: [Add from credentials]
```

#### Slack Configuration
```
Workspace: your-workspace
Credential: [Add Slack token]
Default channel: #ci-cd
```

### 3. Credentials Setup

Navigate to `Manage Jenkins > Manage Credentials`:

#### Required Credentials

1. **Database Password**
   - Kind: Secret text
   - ID: `db-password`
   - Secret: Your database password

2. **Docker Registry**
   - Kind: Username with password
   - ID: `docker-registry-credentials`
   - Username: Your registry username
   - Password: Your registry password

3. **SonarQube Token**
   - Kind: Secret text
   - ID: `sonarqube-token`
   - Secret: Your SonarQube authentication token

4. **Slack Token**
   - Kind: Secret text
   - ID: `slack-token`
   - Secret: Your Slack bot token

5. **SSH Keys for Deployment**
   - Kind: SSH Username with private key
   - ID: `deployment-ssh-key`
   - Username: deploy
   - Private Key: Your deployment SSH private key

## Pipeline Features

### Automated Stages

1. **Checkout**: Source code retrieval from Git
2. **Setup Environment**: Python virtual environment and dependencies
3. **Code Quality Analysis**: Linting, formatting, type checking
4. **Security Analysis**: Vulnerability scanning with Bandit and Safety
5. **Unit Tests**: Automated testing with coverage reporting
6. **Integration Tests**: API endpoint testing
7. **SonarQube Analysis**: Code quality metrics
8. **Quality Gate**: Automated quality checks
9. **Docker Build**: Container image creation
10. **Security Scan**: Container vulnerability scanning
11. **Registry Push**: Image deployment to registry
12. **Staging Deployment**: Automated staging deployment
13. **Smoke Tests**: Post-deployment verification
14. **Production Deployment**: Manual approval for production
15. **Production Verification**: Final smoke tests

### Branch Strategy

- **main**: Production deployments with manual approval
- **develop**: Automatic staging deployments
- **feature/***: Code quality checks and testing only
- **Pull Requests**: Full pipeline without deployment

## Environment Setup

### Environment Variables

Update the following variables in the Jenkinsfile:

```groovy
environment {
    // Update these values for your environment
    DOCKER_REGISTRY = 'your-docker-registry.com'
    STAGING_SERVER = 'staging.smchitfund.com'
    PRODUCTION_SERVER = 'api.smchitfund.com'
    
    // Database configuration
    DB_HOST = 'your-db-host'
    DB_PORT = '3306'
    DB_NAME = 'test_smchitfund'
    DB_USER = 'test_user'
}
```

### Test Database Setup

Create a test database for integration tests:

```sql
CREATE DATABASE test_smchitfund;
CREATE USER 'test_user'@'%' IDENTIFIED BY 'test_password';
GRANT ALL PRIVILEGES ON test_smchitfund.* TO 'test_user'@'%';
FLUSH PRIVILEGES;
```

## Security Configuration

### Container Security

The pipeline includes multiple security scanning layers:

1. **Dependency Scanning**: Safety checks for known vulnerabilities
2. **Code Security**: Bandit static analysis for security issues
3. **Container Scanning**: Trivy scans for container vulnerabilities

### Security Best Practices

1. Store all sensitive data in Jenkins credentials
2. Use non-root user in Docker containers
3. Implement proper network segmentation
4. Regular security updates for base images
5. Enable audit logging for all deployments

## Deployment Configuration

### Docker Deployment

The pipeline supports multiple deployment strategies:

#### 1. Simple Docker Run (Default)
```bash
docker run -d \
    --name ${APP_NAME}-prod \
    -p ${APP_PORT}:8000 \
    -e DATABASE_URL=$PRODUCTION_DATABASE_URL \
    -e ENVIRONMENT=production \
    --restart unless-stopped \
    ${DOCKER_REGISTRY}/${DOCKER_IMAGE_FULL}
```

#### 2. Docker Compose
```bash
# Update docker-compose.yml for your environment
docker-compose up -d
```

#### 3. Kubernetes (Advanced)
```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

### Server Requirements

#### Staging Server
- Docker installed
- SSH access for deployment user
- Network access to database
- Minimum 2GB RAM, 2 CPU cores

#### Production Server
- Docker installed
- SSH access for deployment user
- Network access to database
- Minimum 4GB RAM, 4 CPU cores
- SSL certificates configured
- Backup strategy implemented

## Monitoring and Notifications

### Slack Notifications

The pipeline sends notifications for:
- Successful production deployments
- Pipeline failures
- Quality gate failures
- Security vulnerabilities

### Monitoring Setup

1. **Application Monitoring**: Implement health checks
2. **Log Aggregation**: Centralized logging with ELK stack
3. **Metrics Collection**: Prometheus and Grafana
4. **Alerting**: PagerDuty or similar for critical issues

### Health Checks

The application includes built-in health checks:
- `/api/` - Basic health endpoint
- `/docs` - API documentation availability
- Database connectivity checks

## Troubleshooting

### Common Issues

#### 1. Python Environment Issues
```bash
# Solution: Ensure Python 3.11 is available
python3 --version
pip3 --version
```

#### 2. Docker Build Failures
```bash
# Check Docker daemon
docker info

# Clean up old images
docker system prune -f
```

#### 3. Database Connection Issues
```bash
# Test database connectivity
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD -e "SELECT 1"
```

#### 4. SonarQube Connection Issues
```bash
# Test SonarQube connectivity
curl -u $SONAR_TOKEN: http://sonarqube-server:9000/api/system/status
```

### Pipeline Debugging

#### Enable Debug Mode
```groovy
// Add to pipeline environment
DEBUG = 'true'
VERBOSE = 'true'
```

#### View Detailed Logs
```bash
# Check Jenkins console output
# Enable verbose logging in pipeline stages
```

### Performance Optimization

#### 1. Parallel Execution
The pipeline runs multiple stages in parallel:
- Code quality checks
- Security scans
- Test execution

#### 2. Caching
- Docker layer caching
- Python package caching
- SonarQube analysis caching

#### 3. Resource Management
- Limit concurrent builds
- Clean up workspace after builds
- Optimize Docker image sizes

## Maintenance

### Regular Tasks

1. **Weekly**:
   - Review pipeline performance metrics
   - Update security scanning rules
   - Check for plugin updates

2. **Monthly**:
   - Update base Docker images
   - Review and update dependencies
   - Security audit of pipeline configuration

3. **Quarterly**:
   - Jenkins version updates
   - Pipeline optimization review
   - Disaster recovery testing

### Backup Strategy

1. **Jenkins Configuration**: Regular backup of Jenkins home
2. **Pipeline Scripts**: Version controlled in Git
3. **Credentials**: Secure backup of credential store
4. **Build Artifacts**: Retention policy for build artifacts

## Support

For issues with the Jenkins pipeline:

1. Check the troubleshooting section above
2. Review Jenkins console logs
3. Contact the DevOps team
4. Create an issue in the project repository

## Additional Resources

- [Jenkins Documentation](https://www.jenkins.io/doc/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [SonarQube Documentation](https://docs.sonarqube.org/)
# Quick Start Guide - Jenkins Pipeline

## 🚨 **Immediate Fix for Python Tool Error**

If you're getting the error: `Invalid tool type "python"`, follow these steps:

### **Option 1: Use Simplified Pipeline (Recommended)**

Replace your current Jenkinsfile with the simplified version:

```bash
# Backup current Jenkinsfile
cp Jenkinsfile Jenkinsfile.backup

# Use the simplified version
cp Jenkinsfile.simple Jenkinsfile
```

### **Option 2: Install Python Plugin**

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Click **Available** tab
3. Search for "**Python Plugin**"
4. Install and restart Jenkins

### **Option 3: Manual Fix (Already Done)**

The main Jenkinsfile has been updated to remove the Python tool dependency and handle Python installation manually.

## 🔧 **Minimum Jenkins Setup**

### **Required Plugins**
```
- Pipeline
- Git
- Docker Pipeline
- JUnit (for test results)
```

### **Required Credentials**
```
- db-password (Secret text)
```

### **Environment Variables to Update**
Edit the Jenkinsfile and update these values:
```groovy
DOCKER_REGISTRY = 'your-docker-registry.com'
STAGING_SERVER = 'staging.smchitfund.com'
PRODUCTION_SERVER = 'api.smchitfund.com'
```

## 🚀 **Quick Test**

### **1. Test Locally First**
```bash
# On Windows
.\scripts\local-ci.ps1

# On Linux/Mac
chmod +x scripts/local-ci.sh
./scripts/local-ci.sh
```

### **2. Create Jenkins Job**
1. **New Item** → **Pipeline**
2. **Pipeline Definition**: Pipeline script from SCM
3. **SCM**: Git
4. **Repository URL**: Your Git repository
5. **Script Path**: `Jenkinsfile` (or `Jenkinsfile.simple`)

### **3. Test Pipeline**
1. **Build Now**
2. Check **Console Output** for any issues
3. Fix any missing dependencies on Jenkins agent

## 📋 **Common Issues & Quick Fixes**

### **Missing Context Variable Error**
**Error**: `Required context class hudson.FilePath is missing`

**Fix**: This has been resolved in the updated Jenkinsfiles. All `sh` steps in `post` sections are now properly wrapped in `script` blocks.

### **Python Not Found**
```bash
# Install Python on Jenkins agent
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Or on CentOS/RHEL
sudo yum install python3 python3-pip
```

### **Docker Not Available**
```bash
# Install Docker on Jenkins agent
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker jenkins
```

### **Permission Issues**
```bash
# Give Jenkins user proper permissions
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

## 🎯 **Pipeline Stages Overview**

The simplified pipeline includes:

1. ✅ **Checkout** - Get source code
2. ✅ **Setup Environment** - Python virtual environment
3. ✅ **Code Quality** - Linting, formatting, type checking
4. ✅ **Security Scan** - Bandit and Safety checks
5. ✅ **Tests** - Unit tests with coverage
6. ✅ **Docker Build** - Container image creation
7. ✅ **Deploy** - Staging and production deployment

## 📞 **Need Help?**

1. **Check Console Output**: Look for specific error messages
2. **Review Logs**: Check Jenkins agent logs
3. **Test Locally**: Use the local CI scripts first
4. **Check Dependencies**: Ensure Python, Docker, Git are installed

## 🔄 **Next Steps**

Once the basic pipeline is working:

1. **Add SonarQube** integration (optional)
2. **Configure Slack** notifications (optional)
3. **Set up proper** deployment servers
4. **Add more** security scanning tools
5. **Implement** proper secret management

## 📚 **Full Documentation**

For complete setup instructions, see: `JENKINS_SETUP.md`
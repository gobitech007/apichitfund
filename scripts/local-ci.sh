#!/bin/bash

# Local CI Script for SM ChitFund Python API
# This script runs the same checks as the Jenkins pipeline locally

set -e  # Exit on any error

echo "🚀 Starting Local CI Pipeline for SM ChitFund Python API"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
print_status "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
print_status "Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "🔍 Code Quality Analysis"
echo "========================"

# Linting with Flake8
print_status "Running Flake8 linting..."
if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics; then
    print_success "Flake8 critical checks passed"
else
    print_error "Flake8 critical checks failed"
    exit 1
fi

if flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics; then
    print_success "Flake8 style checks completed"
else
    print_warning "Flake8 style warnings found"
fi

# Code formatting check with Black
print_status "Checking code formatting with Black..."
if black --check --diff .; then
    print_success "Code formatting is correct"
else
    print_warning "Code formatting issues found. Run 'black .' to fix"
fi

# Import sorting check with isort
print_status "Checking import sorting with isort..."
if isort --check-only --diff .; then
    print_success "Import sorting is correct"
else
    print_warning "Import sorting issues found. Run 'isort .' to fix"
fi

# Type checking with MyPy
print_status "Running type checking with MyPy..."
if mypy . --ignore-missing-imports; then
    print_success "Type checking passed"
else
    print_warning "Type checking issues found"
fi

echo ""
echo "🔒 Security Analysis"
echo "===================="

# Security scan with Bandit
print_status "Running security analysis with Bandit..."
if bandit -r . -f json -o bandit-report.json; then
    print_success "Security scan completed"
else
    print_warning "Security issues found. Check bandit-report.json"
fi

# Dependency security check with Safety
print_status "Checking dependencies for security vulnerabilities..."
if safety check --json --output safety-report.json; then
    print_success "Dependency security check passed"
else
    print_warning "Security vulnerabilities found in dependencies. Check safety-report.json"
fi

echo ""
echo "🧪 Testing"
echo "=========="

# Unit tests with coverage
print_status "Running unit tests with coverage..."
if pytest test_*.py -v --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing --junitxml=test-results.xml; then
    print_success "Unit tests passed"
else
    print_error "Unit tests failed"
    exit 1
fi

echo ""
echo "🐳 Docker Build Test"
echo "===================="

# Test Docker build
print_status "Testing Docker build..."
if docker build -t smchitfund-api-test -f Dockerfile.prod .; then
    print_success "Docker build successful"
    
    # Clean up test image
    docker rmi smchitfund-api-test
else
    print_error "Docker build failed"
    exit 1
fi

echo ""
echo "📊 Reports Generated"
echo "===================="
echo "• Test Results: test-results.xml"
echo "• Coverage Report: htmlcov/index.html"
echo "• Coverage XML: coverage.xml"
echo "• Security Report: bandit-report.json"
echo "• Safety Report: safety-report.json"

echo ""
print_success "🎉 Local CI Pipeline Completed Successfully!"
echo ""
echo "Next steps:"
echo "1. Review coverage report: open htmlcov/index.html"
echo "2. Check security reports if warnings were found"
echo "3. Fix any formatting issues with 'black .' and 'isort .'"
echo "4. Commit your changes and push to trigger Jenkins pipeline"

# Deactivate virtual environment
deactivate
# Local CI Script for SM ChitFund Python API (PowerShell)
# This script runs the same checks as the Jenkins pipeline locally

param(
    [switch]$SkipTests,
    [switch]$SkipSecurity,
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Starting Local CI Pipeline for SM ChitFund Python API" -ForegroundColor Blue
Write-Host "===========================================================" -ForegroundColor Blue

# Function to print colored output
function Write-Status {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param($Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

try {
    # Check if virtual environment exists
    if (-not (Test-Path "venv")) {
        Write-Status "Creating virtual environment..."
        python -m venv venv
    }

    # Activate virtual environment
    Write-Status "Activating virtual environment..."
    & "venv\Scripts\Activate.ps1"

    # Upgrade pip
    Write-Status "Upgrading pip..."
    python -m pip install --upgrade pip

    # Install dependencies
    Write-Status "Installing dependencies..."
    pip install -r requirements.txt

    # Install development dependencies
    Write-Status "Installing development dependencies..."
    pip install -r requirements-dev.txt

    Write-Host ""
    Write-Host "🔍 Code Quality Analysis" -ForegroundColor Blue
    Write-Host "========================" -ForegroundColor Blue

    # Linting with Flake8
    Write-Status "Running Flake8 linting..."
    try {
        flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
        Write-Success "Flake8 critical checks passed"
    }
    catch {
        Write-Error "Flake8 critical checks failed"
        throw
    }

    try {
        flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
        Write-Success "Flake8 style checks completed"
    }
    catch {
        Write-Warning "Flake8 style warnings found"
    }

    # Code formatting check with Black
    Write-Status "Checking code formatting with Black..."
    try {
        black --check --diff .
        Write-Success "Code formatting is correct"
    }
    catch {
        Write-Warning "Code formatting issues found. Run 'black .' to fix"
    }

    # Import sorting check with isort
    Write-Status "Checking import sorting with isort..."
    try {
        isort --check-only --diff .
        Write-Success "Import sorting is correct"
    }
    catch {
        Write-Warning "Import sorting issues found. Run 'isort .' to fix"
    }

    # Type checking with MyPy
    Write-Status "Running type checking with MyPy..."
    try {
        mypy . --ignore-missing-imports
        Write-Success "Type checking passed"
    }
    catch {
        Write-Warning "Type checking issues found"
    }

    if (-not $SkipSecurity) {
        Write-Host ""
        Write-Host "🔒 Security Analysis" -ForegroundColor Blue
        Write-Host "====================" -ForegroundColor Blue

        # Security scan with Bandit
        Write-Status "Running security analysis with Bandit..."
        try {
            bandit -r . -f json -o bandit-report.json
            Write-Success "Security scan completed"
        }
        catch {
            Write-Warning "Security issues found. Check bandit-report.json"
        }

        # Dependency security check with Safety
        Write-Status "Checking dependencies for security vulnerabilities..."
        try {
            safety check --json --output safety-report.json
            Write-Success "Dependency security check passed"
        }
        catch {
            Write-Warning "Security vulnerabilities found in dependencies. Check safety-report.json"
        }
    }

    if (-not $SkipTests) {
        Write-Host ""
        Write-Host "🧪 Testing" -ForegroundColor Blue
        Write-Host "==========" -ForegroundColor Blue

        # Unit tests with coverage
        Write-Status "Running unit tests with coverage..."
        try {
            pytest test_*.py -v --cov=. --cov-report=xml --cov-report=html --cov-report=term-missing --junitxml=test-results.xml
            Write-Success "Unit tests passed"
        }
        catch {
            Write-Error "Unit tests failed"
            throw
        }
    }

    if (-not $SkipDocker) {
        Write-Host ""
        Write-Host "🐳 Docker Build Test" -ForegroundColor Blue
        Write-Host "====================" -ForegroundColor Blue

        # Test Docker build
        Write-Status "Testing Docker build..."
        try {
            docker build -t smchitfund-api-test -f Dockerfile.prod .
            Write-Success "Docker build successful"
            
            # Clean up test image
            docker rmi smchitfund-api-test
        }
        catch {
            Write-Error "Docker build failed"
            throw
        }
    }

    Write-Host ""
    Write-Host "📊 Reports Generated" -ForegroundColor Blue
    Write-Host "===================" -ForegroundColor Blue
    Write-Host "• Test Results: test-results.xml"
    Write-Host "• Coverage Report: htmlcov/index.html"
    Write-Host "• Coverage XML: coverage.xml"
    if (-not $SkipSecurity) {
        Write-Host "• Security Report: bandit-report.json"
        Write-Host "• Safety Report: safety-report.json"
    }

    Write-Host ""
    Write-Success "🎉 Local CI Pipeline Completed Successfully!"
    Write-Host ""
    Write-Host "Next steps:"
    Write-Host "1. Review coverage report: htmlcov/index.html"
    if (-not $SkipSecurity) {
        Write-Host "2. Check security reports if warnings were found"
    }
    Write-Host "3. Fix any formatting issues with 'black .' and 'isort .'"
    Write-Host "4. Commit your changes and push to trigger Jenkins pipeline"

}
catch {
    Write-Error "Local CI Pipeline failed: $_"
    exit 1
}
finally {
    # Deactivate virtual environment
    if (Get-Command deactivate -ErrorAction SilentlyContinue) {
        deactivate
    }
}
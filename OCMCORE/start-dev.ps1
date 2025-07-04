# PowerShell script to start Django dev server with Memcached support
# Usage: .\start-dev.ps1 [memcached|local]

param(
    [string]$Mode = "memcached"
)

Write-Host "Starting Django development environment..." -ForegroundColor Green

# Load environment variables from .env if present
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^(\w+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2])
        }
    }
    Write-Host "Loaded environment variables from .env" -ForegroundColor Yellow
}

# Default to 8000 if not set
$port = $env:DJANGO_RUNSERVER_PORT
if (-not $port) { $port = 8000 }

# Check if Docker is available
$dockerAvailable = $false
try {
    docker --version | Out-Null
    $dockerAvailable = $true
    Write-Host "Docker is available" -ForegroundColor Green
} catch {
    Write-Host "Docker not available - will use local Memcached if installed" -ForegroundColor Yellow
}

# Start Memcached based on mode
if ($Mode -eq "memcached" -and $dockerAvailable) {
    Write-Host "Starting Memcached with Docker..." -ForegroundColor Green
    
    # Check if Memcached container is already running
    $memcachedRunning = docker ps --filter "name=memcached" --format "table {{.Names}}" | Select-String "memcached"
    
    if (-not $memcachedRunning) {
        Write-Host "Starting Memcached container..." -ForegroundColor Yellow
        docker-compose -f docker-compose.dev.yml up -d memcached
        
        # Wait a moment for Memcached to start
        Start-Sleep -Seconds 3
        
        # Test Memcached connection
        try {
            $testResult = python -c "import socket; s = socket.socket(); s.connect(('localhost', 11211)); s.close(); print('Memcached is running')" 2>$null
            if ($testResult) {
                Write-Host "✅ Memcached is running and accessible" -ForegroundColor Green
            }
        } catch {
            Write-Host "⚠️  Memcached may not be ready yet, but continuing..." -ForegroundColor Yellow
        }
    } else {
        Write-Host "✅ Memcached container is already running" -ForegroundColor Green
    }
} elseif ($Mode -eq "local") {
    Write-Host "Using local Memcached installation (if available)" -ForegroundColor Yellow
    Write-Host "Make sure Memcached is installed and running on localhost:11211" -ForegroundColor Yellow
} else {
    Write-Host "No Memcached mode specified or Docker not available" -ForegroundColor Yellow
    Write-Host "Caching will be disabled. Use 'memcached' or 'local' mode for caching support." -ForegroundColor Yellow
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\venv\Scripts\Activate.ps1

# Test Memcached connection if in memcached mode
if ($Mode -eq "memcached") {
    Write-Host "Testing Memcached connection..." -ForegroundColor Yellow
    python test_memcached.py
}

Write-Host "Starting Django development server on port $port..." -ForegroundColor Green
Write-Host "Access your app at: http://localhost:$port" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:$port/swagger/" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

# Start Django dev server on the specified port
python manage.py runserver 0.0.0.0:$port 
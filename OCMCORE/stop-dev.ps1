# PowerShell script to stop Django development environment and clean up
# Usage: .\stop-dev.ps1

Write-Host "Stopping Django development environment..." -ForegroundColor Green

# Check if Docker is available
try {
    docker --version | Out-Null
    
    # Stop Memcached container
    Write-Host "Stopping Memcached container..." -ForegroundColor Yellow
    docker-compose -f docker-compose.dev.yml down
    
    Write-Host "✅ Development environment stopped" -ForegroundColor Green
} catch {
    Write-Host "Docker not available or not running" -ForegroundColor Yellow
}

Write-Host "Development environment cleanup complete!" -ForegroundColor Green 
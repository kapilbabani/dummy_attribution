# PowerShell script to generate a self-signed SSL certificate for Nginx
# Run as Administrator in the project root

$certDir = "nginx/certs"
New-Item -ItemType Directory -Force -Path $certDir | Out-Null

$certPath = "$certDir/server.crt"
$keyPath = "$certDir/server.key"

# Check for OpenSSL
$openssl = "openssl"
if (-not (Get-Command $openssl -ErrorAction SilentlyContinue)) {
    Write-Host "OpenSSL is not installed. Downloading and installing Win32 OpenSSL Light..."
    $installerUrl = "https://slproweb.com/download/Win64OpenSSL_Light-3_3_1.exe"
    $installerPath = "$env:TEMP\Win64OpenSSL_Light-3_3_1.exe"
    Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -ArgumentList "/silent" -Wait
    $env:Path += ";C:\Program Files\OpenSSL-Win64\bin"
    if (-not (Get-Command $openssl -ErrorAction SilentlyContinue)) {
        Write-Host "OpenSSL installation failed. Please install manually from https://slproweb.com/products/Win32OpenSSL.html."
        exit 1
    }
    Write-Host "OpenSSL installed successfully."
}

& $openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout $keyPath -out $certPath -subj "/CN=localhost"

Write-Host "Self-signed certificate generated at $certPath and $keyPath." 
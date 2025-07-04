# One-time setup script for Windows Server: Docker Engine + GitHub Actions Runner
# Run as Administrator

# 1. Install Docker Engine (not Docker Desktop)
Write-Host "Installing Docker Engine..."
Install-Module -Name DockerMsftProvider -Repository PSGallery -Force
Install-Package -Name docker -ProviderName DockerMsftProvider -Force
Start-Service docker
Write-Host "Docker Engine installed and started."

# 2. Download and configure GitHub Actions self-hosted runner
$runnerVersion = "2.316.0"
$runnerDir = "C:\actions-runner"
$repoUrl = "https://github.com/OWNER/REPO"  # <-- CHANGE THIS
$runnerToken = "YOUR_RUNNER_TOKEN"           # <-- CHANGE THIS

Write-Host "Setting up GitHub Actions runner..."
New-Item -ItemType Directory -Force -Path $runnerDir | Out-Null
cd $runnerDir

Invoke-WebRequest -Uri "https://github.com/actions/runner/releases/download/v$runnerVersion/actions-runner-win-x64-$runnerVersion.zip" -OutFile "actions-runner.zip"
Expand-Archive -Path "actions-runner.zip" -DestinationPath $runnerDir

# 3. Configure the runner
./config.cmd --url $repoUrl --token $runnerToken --unattended --name "windows-runner-01"

# 4. Install runner as a service
./svc install
./svc start

Write-Host "GitHub Actions runner installed and started as a service." 
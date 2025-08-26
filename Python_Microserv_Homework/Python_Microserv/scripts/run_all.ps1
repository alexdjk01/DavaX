<#
Run everything for the project on Windows PowerShell:

- Ensures Docker/Redis (container "pm_redis") is running on localhost:6379
- Sets environment variables for streaming
- Installs Python dependencies from requirements.txt if needed
- Starts the FastAPI server (uvicorn) in a new PowerShell window
- Starts the Redis stream consumer in another new PowerShell window
- Opens the dashboard (index.html) in your default browser

Usage:
  .\scripts\run_all.ps1
#>

function Require-Command($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Write-Error "Required command '$name' not found in PATH."
    exit 1
  }
}

# Resolve paths
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir         # ...\Python_Microserv
$Dashboard = Join-Path $ProjectRoot "dashboard\index.html"
$RequirementsFile = Join-Path $ProjectRoot "requirements.txt"

# 1) Ensure Docker/Redis is running
Require-Command docker
$containerName = "pm_redis"
$redisRunning = (docker ps --filter "name=$containerName" --format "{{.Names}}") -ne $null
$redisExists  = (docker ps -a --filter "name=$containerName" --format "{{.Names}}") -ne $null

if (-not $redisExists) {
  Write-Host "Starting new Redis container '$containerName' on port 6379..."
  docker run -d --name $containerName -p 6379:6379 redis:7 | Out-Null
} elseif (-not $redisRunning) {
  Write-Host "Starting existing Redis container '$containerName'..."
  docker start $containerName | Out-Null
} else {
  Write-Host "Redis container '$containerName' is already running."
}

# 2) Set environment variables for this session
$env:STREAM_BACKEND = "REDIS"
$env:REDIS_URL = "redis://localhost:6379/0"
if (-not $env:REDIS_STREAM_KEY) { $env:REDIS_STREAM_KEY = "ops_stream" }

# 3) Install dependencies if needed
if (Test-Path $RequirementsFile) {
  Write-Host "Installing dependencies from $RequirementsFile..."
  pip install --upgrade pip
  pip install -r $RequirementsFile
} else {
  Write-Warning "No requirements.txt found at $RequirementsFile"
}

# 4) Start FastAPI server in a new PowerShell window
$apiCmd = 'python -m uvicorn application.main:app --reload'
$apiWorkDir = $ProjectRoot
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location `"$apiWorkDir`"; $apiCmd"

# 5) Start Redis stream consumer in another new PowerShell window
$consumerCmd = 'python -m application.utils.stream_consumer_redis'
Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "Set-Location `"$apiWorkDir`"; $consumerCmd"

# 6) Open the dashboard in the default browser
if (Test-Path $Dashboard) {
  Start-Process $Dashboard
} else {
  Write-Warning "Dashboard not found at: $Dashboard"
}

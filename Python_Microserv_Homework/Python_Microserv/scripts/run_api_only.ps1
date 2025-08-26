<#
Start only the FastAPI app with Redis streaming enabled (Windows PowerShell).

Usage:
  .\run_api_only.ps1
#>
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Env vars for the session
$env:STREAM_BACKEND = "REDIS"
$env:REDIS_URL = "redis://localhost:6379/0"
if (-not $env:REDIS_STREAM_KEY) { $env:REDIS_STREAM_KEY = "ops_stream" }

Set-Location $ProjectRoot
python -m uvicorn application.main:app --reload

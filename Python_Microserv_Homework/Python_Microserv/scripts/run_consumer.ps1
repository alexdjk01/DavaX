<#
Start the Redis stream consumer demo (Windows PowerShell).

Usage:
  .\run_consumer.ps1
#>
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

Set-Location $ProjectRoot
python -m application.utils.stream_consumer_redis

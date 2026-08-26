<# Prepares the PRIMUS zero-prior continual-learning trainer. #>
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'Run .\setup.ps1 first.' }
& $Python -m pip install --upgrade torch
& $Python -m src.training.meta_rl --help
Write-Host '[PRIMUS] Meta-RL trainer ready.'
Write-Host '[PRIMUS] Teach and use at least two tasks several times, then train with:'
Write-Host '  .\.venv\Scripts\python.exe -m src.training.meta_rl'
Write-Host '[PRIMUS] Resume continual learning with --resume.'

<# Starts PRIMUS on Windows. Open http://127.0.0.1:7860 after it starts. #>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
$Python = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $Python)) { throw 'PRIMUS is not set up yet. Run .\setup.ps1 first.' }

try { Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2 | Out-Null }
catch {
    if (Get-Command ollama -ErrorAction SilentlyContinue) {
        Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden
        Start-Sleep -Seconds 2
    } else { Write-Warning 'Ollama is not installed. PRIMUS will use its built-in fallback for normal chat.' }
}

Write-Host '[PRIMUS] Starting dashboard at http://127.0.0.1:7860'
& $Python app.py

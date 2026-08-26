<# Sets up PRIMUS on Windows 10/11. Run: .\setup.ps1 #>
[CmdletBinding()]
param(
    [switch]$SkipOllama,
    [switch]$SkipVoice,
    [switch]$SkipCppBuild
)

$ErrorActionPreference = 'Stop'
$ProjectRoot = $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot '.venv'
$Python = Join-Path $VenvPath 'Scripts\python.exe'
$DataPath = Join-Path $ProjectRoot 'data'

function Get-PythonCommand {
    $candidates = @('py -3.11', 'py -3.12', 'python')
    foreach ($candidate in $candidates) {
        try {
            $version = Invoke-Expression "$candidate --version" 2>$null
            if ($LASTEXITCODE -eq 0 -and $version -match 'Python 3\.(1[01]|12)') { return $candidate }
        } catch { }
    }
    throw 'Python 3.10, 3.11, or 3.12 is required. Install it, then run setup.ps1 again.'
}

function Test-OllamaReady {
    try { return (Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2).StatusCode -eq 200 }
    catch { return $false }
}

Set-Location $ProjectRoot
if (-not (Test-Path $Python)) {
    Write-Host '[PRIMUS] Creating Python virtual environment...'
    $PythonCommand = Get-PythonCommand
    Invoke-Expression "$PythonCommand -m venv `"$VenvPath`""
}

Write-Host '[PRIMUS] Installing Python dependencies...'
& $Python -m pip install --upgrade pip wheel setuptools
& $Python -m pip install -r requirements.txt

if (-not $SkipCppBuild) {
    if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
        throw 'CMake is required for the C++ engine. Install CMake and Visual Studio Build Tools (Desktop development with C++), or rerun with -SkipCppBuild.'
    }
    Write-Host '[PRIMUS] Building C++ neural core...'
    $PybindCmakeDir = & $Python -m pybind11 --cmakedir
    cmake -S cpp_core -B cpp_core/build -DCMAKE_BUILD_TYPE=Release "-Dpybind11_DIR=$PybindCmakeDir"
    cmake --build cpp_core/build --config Release
}

if (-not $SkipVoice) {
    Write-Host '[PRIMUS] Downloading Piper voice model...'
    New-Item -ItemType Directory -Force -Path $DataPath | Out-Null
    foreach ($voiceFile in @('en_US-lessac-medium.onnx', 'en_US-lessac-medium.onnx.json')) {
        $target = Join-Path $DataPath $voiceFile
        if (-not (Test-Path $target)) {
            Invoke-WebRequest -Uri "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/$voiceFile" -OutFile $target
        }
    }
}

if (-not $SkipOllama) {
    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw 'Install Ollama from https://ollama.com/download/windows, then rerun setup.ps1.' }
        Write-Host '[PRIMUS] Installing Ollama with winget...'
        winget install --id Ollama.Ollama --exact --accept-source-agreements --accept-package-agreements
        $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    }
    if (-not (Test-OllamaReady)) { Start-Process -FilePath 'ollama' -ArgumentList 'serve' -WindowStyle Hidden }
    Start-Sleep -Seconds 2
    ollama pull qwen2.5:7b-instruct
}

Write-Host '[PRIMUS] Setup complete. Start it with: .\run.ps1'

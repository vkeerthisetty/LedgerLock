param(
    [switch]$IncludeFloci
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$tempRoot = Join-Path $repoRoot ".test-tmp"

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create .venv and install requirements-dev.txt first."
}

Push-Location $repoRoot
try {
    New-Item -ItemType Directory -Force $tempRoot | Out-Null

    git diff --check HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "Git whitespace validation failed."
    }

    & $python -m unittest discover -s tests -v
    if ($LASTEXITCODE -ne 0) {
        throw "Unittest suite failed."
    }

    & $python -m pytest -q -p no:cacheprovider --basetemp="$tempRoot\pytest"
    if ($LASTEXITCODE -ne 0) {
        throw "Pytest suite failed."
    }

    & $python -m compileall app storage signing logging infra scripts tests
    if ($LASTEXITCODE -ne 0) {
        throw "Python compilation check failed."
    }

    & $python scripts\check_repository_safety.py
    if ($LASTEXITCODE -ne 0) {
        throw "Repository safety scan failed."
    }

    if ($IncludeFloci) {
        & "$PSScriptRoot\run_floci_integration.ps1"
        if ($LASTEXITCODE -ne 0) {
            throw "Floci integration check failed."
        }
    }

    Write-Host "LedgerLock review preflight PASSED." -ForegroundColor Green
}
finally {
    Pop-Location
    if (Test-Path $tempRoot) {
        Remove-Item -LiteralPath $tempRoot -Recurse -Force
    }
}

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$docker = Get-Command docker -ErrorAction SilentlyContinue

if (-not $docker) {
    $userDocker = Join-Path $env:LOCALAPPDATA "Programs\DockerDesktop\resources\bin\docker.exe"
    if (Test-Path $userDocker) {
        $docker = $userDocker
        $dockerBin = Split-Path -Parent $userDocker
        $env:Path = "$dockerBin;$env:Path"
    }
    else {
        throw "Docker CLI not found. Start Docker Desktop and reopen the terminal."
    }
}

if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Create .venv and install requirements-dev.txt first."
}

$env:USE_CLOUD_SERVICES = "true"
$env:GCP_PROJECT_ID = "floci-local"
$env:GOOGLE_CLOUD_PROJECT = "floci-local"
$env:GCP_REGION = "us-central1"
$env:FLOCI_GCP_ENDPOINT = "http://localhost:4588"
$env:FIRESTORE_EMULATOR_HOST = "localhost:4588"
$env:FIRESTORE_COLLECTION = "audit_ledger_floci"
$env:KMS_KEY_RING = "ledgerlock-keyring"
$env:KMS_KEY_NAME = "checkpoint-signer"
$env:KMS_KEY_VERSION = "1"
$env:CLOUD_LOG_NAME = "ledgerlock-audit-events"
$env:RUN_FLOCI_INTEGRATION = "true"

Push-Location $repoRoot
try {
    & $docker compose -f docker-compose.floci.yml up -d

    $ready = $false
    foreach ($attempt in 1..30) {
        try {
            $client = [System.Net.Sockets.TcpClient]::new()
            $client.Connect("localhost", 4588)
            $client.Dispose()
            $ready = $true
            break
        }
        catch {
            if ($client) {
                $client.Dispose()
            }
            Start-Sleep -Seconds 1
        }
    }

    if (-not $ready) {
        throw "Floci-GCP did not become reachable on localhost:4588. Run docker compose logs floci-gcp."
    }

    & $python infra\bootstrap_floci.py
    & $python -m pytest tests\test_floci_integration.py -v -p no:cacheprovider
    if ($LASTEXITCODE -ne 0) {
        throw "Floci integration test failed with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

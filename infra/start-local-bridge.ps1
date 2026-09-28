$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $repo '.local-bridge'
New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$python = Join-Path $repo 'backend/.venv/Scripts/python.exe'
$cloudflared = Join-Path $runtime 'cloudflared.exe'
if (!(Test-Path $cloudflared)) { throw 'Install cloudflared.exe in .local-bridge first.' }
if (Get-NetTCPConnection -LocalPort 8001 -State Listen -ErrorAction SilentlyContinue) {
    throw 'Port 8001 is already in use. Stop the existing bridge before starting another.'
}
try { Invoke-RestMethod 'http://127.0.0.1:11434/api/tags' -TimeoutSec 3 | Out-Null }
catch {
    $ollama = Join-Path $env:LOCALAPPDATA 'Programs/Ollama/ollama.exe'
    Start-Process $ollama -ArgumentList 'serve' -WindowStyle Hidden
}

# Retrieve only this application's existing secrets; never print their values.
$config = az containerapp show -g multimodal-rag-rg -n multimodal-rag-backend -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Could not read Azure application configuration.' }
$secrets = az containerapp secret list -g multimodal-rag-rg -n multimodal-rag-backend --show-values -o json | ConvertFrom-Json
if ($LASTEXITCODE -ne 0) { throw 'Could not read Azure application secrets.' }
foreach ($setting in $config.properties.template.containers[0].env) {
    if ($setting.name -in @('DATABASE_URL','AZURE_STORAGE_CONNECTION_STRING','AZURE_STORAGE_CONTAINER','STORAGE_BACKEND')) {
        $value = $setting.value
        if ($setting.secretRef) { $value = ($secrets | Where-Object name -eq $setting.secretRef).value }
        [Environment]::SetEnvironmentVariable($setting.name, $value, 'Process')
    }
}
$keyPath = Join-Path $runtime 'access-key.txt'
if (!(Test-Path $keyPath)) {
    $bytes = New-Object byte[] 32
    $rng = [Security.Cryptography.RandomNumberGenerator]::Create()
    $rng.GetBytes($bytes)
    [Convert]::ToBase64String($bytes) | Set-Content -LiteralPath $keyPath -NoNewline
    $rng.Dispose()
}
$env:LOCAL_BRIDGE_TOKEN = (Get-Content -Raw -LiteralPath $keyPath).Trim()
$env:DEPLOYMENT_MODE = 'local_full'
$env:FRONTEND_ORIGIN = 'https://agreeable-bay-0a770bc0f.2.azurestaticapps.net'
$env:CORS_ORIGINS = $env:FRONTEND_ORIGIN
$env:TRUSTED_HOSTS = '127.0.0.1,localhost'
$env:OLLAMA_BASE_URL = 'http://127.0.0.1:11434'
$env:LLM_PROVIDER = 'ollama'
$env:GENERATION_MODEL = 'qwen3:8b'
$env:VERIFICATION_MODEL = 'qwen3:8b'
$env:CONVERSATION_REWRITE_MODEL = 'qwen3:8b'
$env:CONVERSATION_SUMMARY_MODEL = 'qwen3:8b'
$env:STORAGE_ROOT = Join-Path $repo 'storage'
$env:TEXT_EMBEDDING_DEVICE = 'cuda'
$env:CLIP_DEVICE = 'cuda'
$env:RERANKER_DEVICE = 'cuda'
# A local SQLite queue avoids provisioning a cloud broker for this single worker.
$queuePath = (Join-Path $runtime 'queue.sqlite').Replace('\','/')
$resultPath = (Join-Path $runtime 'results.sqlite').Replace('\','/')
$env:CELERY_BROKER_URL = "sqla+sqlite:///$queuePath"
$env:CELERY_RESULT_BACKEND = "db+sqlite:///$resultPath"
$backend = Join-Path $repo 'backend'
$api = Start-Process $python -ArgumentList '-m uvicorn app.local_bridge:app --host 127.0.0.1 --port 8001' -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'api.log') -RedirectStandardError (Join-Path $runtime 'api-error.log') -PassThru
$worker = Start-Process $python -ArgumentList '-m celery -A app.worker.celery_app:celery_app worker --pool=solo --concurrency=1 --loglevel=INFO' -WorkingDirectory $backend -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'worker.log') -RedirectStandardError (Join-Path $runtime 'worker-error.log') -PassThru
$tunnel = Start-Process $cloudflared -ArgumentList 'tunnel --url http://127.0.0.1:8001 --http-host-header localhost --no-autoupdate' -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'tunnel.log') -RedirectStandardError (Join-Path $runtime 'tunnel-error.log') -PassThru
@($api,$worker,$tunnel) | ForEach-Object {
    @{id=$_.Id;started=$_.StartTime.ToUniversalTime().ToString('o');name=$_.ProcessName}
} | ConvertTo-Json | Set-Content (Join-Path $runtime 'processes.json')
Write-Output 'Started local API, worker, and tunnel. See .local-bridge for logs and the private access key.'

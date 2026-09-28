$ErrorActionPreference = 'Stop'
$runtime = Join-Path (Split-Path -Parent $PSScriptRoot) '.local-bridge'
$tunnelLog = Get-Content -Raw (Join-Path $runtime 'tunnel-error.log')
$url = [regex]::Match($tunnelLog, 'https://[a-z-]+\.trycloudflare\.com').Value
if (!$url) { throw 'No tunnel URL yet. Wait for cloudflared to start.' }
$key = (Get-Content -Raw (Join-Path $runtime 'access-key.txt')).Trim()
$connection = @{url="$url/api/v1";token=$key} | ConvertTo-Json -Compress
$target = 'https://agreeable-bay-0a770bc0f.2.azurestaticapps.net/#local-bridge=' + [Uri]::EscapeDataString($connection)
$safeTarget = [System.Net.WebUtility]::HtmlEncode($target)
$html = '<!doctype html><meta charset="utf-8"><title>Open local AI workspace</title><h1>Local Ollama workspace</h1><p>Keep this file private: it contains your local access key.</p><a href="' + $safeTarget + '">Open Azure site connected to this computer</a>'
$html | Set-Content -Encoding utf8 (Join-Path $runtime 'connect.html')
Write-Output 'Private launcher saved to .local-bridge/connect.html'

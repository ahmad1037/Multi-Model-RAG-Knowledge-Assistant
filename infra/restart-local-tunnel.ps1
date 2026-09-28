$ErrorActionPreference = 'Stop'
$runtime = Join-Path (Split-Path -Parent $PSScriptRoot) '.local-bridge'
$recordPath = Join-Path $runtime 'processes.json'
$records = @(Get-Content $recordPath | ConvertFrom-Json)
foreach ($record in $records | Where-Object name -eq 'cloudflared') {
    $process = Get-Process -Id $record.id -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq $record.name -and
        $process.StartTime.ToUniversalTime() -eq ([DateTime]$record.started).ToUniversalTime()) {
        taskkill.exe /PID $record.id /T /F | Out-Null
    }
}
$tunnel = Start-Process (Join-Path $runtime 'cloudflared.exe') -ArgumentList 'tunnel --url http://127.0.0.1:8001 --http-host-header localhost --no-autoupdate' -WindowStyle Hidden -RedirectStandardOutput (Join-Path $runtime 'tunnel.log') -RedirectStandardError (Join-Path $runtime 'tunnel-error.log') -PassThru
$records = @($records | Where-Object name -ne 'cloudflared') + @(@{id=$tunnel.Id;started=$tunnel.StartTime.ToUniversalTime().ToString('o');name=$tunnel.ProcessName})
$records | ConvertTo-Json | Set-Content $recordPath
Write-Output 'Tunnel restarted. Regenerate the private launcher once the new tunnel URL appears.'

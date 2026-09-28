$ErrorActionPreference = 'Stop'
$runtime = Join-Path (Split-Path -Parent $PSScriptRoot) '.local-bridge'
$records = Get-Content (Join-Path $runtime 'processes.json') | ConvertFrom-Json
foreach ($record in $records) {
    $process = Get-Process -Id $record.id -ErrorAction SilentlyContinue
    if ($process -and $process.ProcessName -eq $record.name -and
        $process.StartTime.ToUniversalTime() -eq ([DateTime]$record.started).ToUniversalTime()) {
        taskkill.exe /PID $record.id /T /F
    }
}

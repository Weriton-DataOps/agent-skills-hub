# OverCore — roda um ciclo do curador. Use -Live para o modo real (materializa skill + abre PR).
param([switch]$Live)
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..\..")).Path
Set-Location $repoRoot

$script = Join-Path $repoRoot "agents\curator\scripts\run_cycle.py"
$pyArgs = @($script)
if ($Live) { $pyArgs += "--live" }

Write-Output "[OverCore] ciclo do curador em $repoRoot (Live=$Live) $(Get-Date -Format o)"
& python @pyArgs

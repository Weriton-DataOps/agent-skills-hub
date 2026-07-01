# OverCore — registra a tarefa agendada do Windows que roda o ciclo do curador.
#   .\register-task.ps1              # diario 07:00, modo DRY (seguro)
#   .\register-task.ps1 -Time 06:30 -Live   # diario 06:30, modo real (abre PRs)
param(
  [string]$Time = "07:00",
  [switch]$Live
)
$ErrorActionPreference = "Stop"

$runCycle = Join-Path $PSScriptRoot "run-cycle.ps1"
$liveArg = if ($Live) { " -Live" } else { "" }
$argument = "-NoProfile -ExecutionPolicy Bypass -File `"$runCycle`"$liveArg"

$action  = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $argument
$trigger = New-ScheduledTaskTrigger -Daily -At $Time
Register-ScheduledTask -TaskName "OverCore-Curator" -Action $action -Trigger $trigger `
  -Description "OverCore: ciclo diario do curador (ingest -> draft -> judge -> PR). Merge e sempre humano." -Force

Write-Output "Tarefa 'OverCore-Curator' registrada: diaria as $Time (Live=$Live)."
Write-Output "Rodar agora:   Start-ScheduledTask -TaskName OverCore-Curator"
Write-Output "Remover:       Unregister-ScheduledTask -TaskName OverCore-Curator -Confirm:`$false"

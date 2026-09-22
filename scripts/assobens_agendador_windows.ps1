# Alternativa local ao GitHub Actions: agenda a sincronização ASSOBENS no Agendador de Tarefas do Windows
# às 08:00, 12:00 e 17:00 (fuso do sistema, que deve ser E. South America Standard Time = America/Sao_Paulo).
# Uso (PowerShell como o usuário que tem o .env na raiz do repositório):
#   .\scripts\assobens_agendador_windows.ps1            # instala
#   .\scripts\assobens_agendador_windows.ps1 -Remover   # remove
param([switch]$Remover)

$repo = Split-Path -Parent $PSScriptRoot
$python = (Get-Command python).Source
$tz = (Get-TimeZone).Id
if ($tz -ne "E. South America Standard Time") {
  Write-Warning "Fuso do sistema é '$tz'; os horários 08/12/17 seguem o fuso do sistema, não America/Sao_Paulo."
}
foreach ($h in @("08:00", "12:00", "17:00")) {
  $name = "TorreTecar ASSOBENS sync $h"
  if ($Remover) { Unregister-ScheduledTask -TaskName $name -Confirm:$false -ErrorAction SilentlyContinue; continue }
  $action = New-ScheduledTaskAction -Execute $python -Argument "-m assobens sync --trigger scheduler" -WorkingDirectory $repo
  $trigger = New-ScheduledTaskTrigger -Daily -At $h
  $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 40) -StartWhenAvailable
  Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Force | Out-Null
  Write-Host "instalada: $name"
}
if (-not $Remover) { Write-Host "Depois de cada execução local, publique com: git add 'Analityc share' ; git commit -m 'data: ASSOBENS' ; git push" }

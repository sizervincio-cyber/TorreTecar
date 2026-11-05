# Instalacao em uma linha (PowerShell):
#   irm https://raw.githubusercontent.com/sizervincio-cyber/TorreTecar/main/instaladores/instalar-codex.ps1 | iex
# Baixa o pacote torre-tecar-codex.zip deste repositorio, extrai numa pasta temporaria e roda o instalar.ps1.
$ErrorActionPreference = "Stop"
$zipUrl = "https://raw.githubusercontent.com/sizervincio-cyber/TorreTecar/main/instaladores/torre-tecar-codex.zip"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ("torre-codex-" + [Guid]::NewGuid().ToString("N").Substring(0, 8))
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$zip = Join-Path $tmp "torre-tecar-codex.zip"
Write-Host "Baixando o pacote da Torre Tecar para o Codex..."
Invoke-WebRequest -Uri $zipUrl -OutFile $zip -UseBasicParsing
Expand-Archive -Path $zip -DestinationPath $tmp -Force
& (Join-Path $tmp "instalar.ps1")

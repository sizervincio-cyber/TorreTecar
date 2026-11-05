# Instalador da Torre Tecar no Codex (Windows PowerShell 5.1 ou 7).
# - Registra o MCP somente leitura "torre-tecar" no ~/.codex/config.toml (token em variavel de ambiente do usuario)
# - Instala a skill "torre-relatorios" em ~/.codex/skills
# - Testa a conexao com o MCP
# Uso: powershell -ExecutionPolicy Bypass -File .\instalar.ps1 [-Token "torre_..."] [-Url "https://.../mcp"]
param(
  [string]$Token = "",
  [string]$Url = "https://mcp.2-25-95-244.sslip.io/mcp",
  [switch]$NovoToken
)
$ErrorActionPreference = "Stop"
$aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
$codexHome = $env:CODEX_HOME
if (-not $codexHome) { $codexHome = Join-Path $HOME ".codex" }
New-Item -ItemType Directory -Force -Path $codexHome | Out-Null

Write-Host ""
Write-Host "== Torre Tecar para o Codex ==" -ForegroundColor Cyan

# 1) Token (gerado na VPS com deploy/mcp-token.sh). Numa reinstalacao, reaproveita o token ja salvo.
$salvo = [Environment]::GetEnvironmentVariable("TORRE_MCP_TOKEN", "User")
if (-not $Token -and -not $NovoToken -and $salvo -match '^torre_[0-9a-f]{48}$') {
  $Token = $salvo
  Write-Host "Usando o token ja salvo neste computador (para trocar: instalar.ps1 -NovoToken)."
}
if (-not $Token) {
  $seguro = Read-Host "Cole o token do MCP da Torre (gerado na VPS)" -AsSecureString
  $ptr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($seguro)
  try { $Token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($ptr) } finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($ptr) }
}
$Token = $Token.Trim()
if ($Token -notmatch '^torre_[0-9a-f]{48}$') { throw "Token em formato inesperado. Gere um novo na VPS: cd /opt/torre/repo/deploy && ./mcp-token.sh" }
[Environment]::SetEnvironmentVariable("TORRE_MCP_TOKEN", $Token, "User")
$env:TORRE_MCP_TOKEN = $Token
Write-Host "1/4 Token salvo na variavel de ambiente do usuario TORRE_MCP_TOKEN"

# 2) MCP no config.toml (com copia de seguranca)
$config = Join-Path $codexHome "config.toml"
$texto = ""
if (Test-Path $config) {
  Copy-Item $config "$config.bak-torre" -Force
  $texto = [IO.File]::ReadAllText($config)
}
$texto = [regex]::Replace($texto, '(?ms)^\[mcp_servers\.torre-tecar\].*?(?=^\[(?!mcp_servers\.torre-tecar)|\z)', '')
$bloco = @"

[mcp_servers.torre-tecar]
url = "$Url"
bearer_token_env_var = "TORRE_MCP_TOKEN"
startup_timeout_sec = 30
tool_timeout_sec = 120
"@
$texto = $texto.TrimEnd() + "`r`n" + $bloco + "`r`n"
[IO.File]::WriteAllText($config, $texto, (New-Object Text.UTF8Encoding($false)))
Write-Host "2/4 MCP torre-tecar registrado em $config (copia anterior: config.toml.bak-torre)"

# 3) Skill de relatorios
$origem = Join-Path $aqui "skills\torre-relatorios"
$destino = Join-Path $codexHome "skills\torre-relatorios"
if (-not (Test-Path $origem)) { throw "Pasta da skill nao encontrada ao lado do instalador: $origem" }
if (Test-Path $destino) { Remove-Item -Recurse -Force $destino }
New-Item -ItemType Directory -Force -Path (Split-Path $destino) | Out-Null
Copy-Item -Recurse $origem $destino
Write-Host "3/4 Skill torre-relatorios instalada em $destino"

# 4) Teste de conexao
try {
  $corpo = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"instalador-torre","version":"1"}}}'
  $r = Invoke-WebRequest -Uri $Url -Method Post -UseBasicParsing -Body $corpo -ContentType "application/json" `
       -Headers @{ Authorization = "Bearer $Token"; Accept = "application/json, text/event-stream" } -TimeoutSec 30
  Write-Host "4/4 Conexao com o MCP OK (HTTP $($r.StatusCode))" -ForegroundColor Green
} catch {
  $codigo = $null
  if ($_.Exception.Response) { $codigo = [int]$_.Exception.Response.StatusCode }
  if ($codigo -eq 401) { Write-Host "4/4 O MCP recusou o token (401). Gere outro na VPS e rode o instalador de novo." -ForegroundColor Yellow }
  else { Write-Host "4/4 Nao consegui falar com o MCP agora ($($_.Exception.Message)). A instalacao ficou feita; teste de novo quando a rota estiver no ar." -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "Pronto. Feche e abra o Codex para ele ler o token e a skill." -ForegroundColor Cyan
Write-Host "Teste no Codex: 'Use o MCP torre-tecar e me diga ate quando vao as bases.'"

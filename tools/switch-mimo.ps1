# 切换到 MiMo V2.5 Pro 环境
# 用法：. .\tools\switch-mimo.ps1 然后执行 claude
# API Key 从 .env 读取

$envFile = Join-Path $PSScriptRoot "..\.env"
$token = ""
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*MIMO_AUTH_TOKEN\s*=\s*(.+?)\s*$') { $token = $Matches[1] }
    }
}
if (-not $token) { Write-Host "请在 .env 中填写 MIMO_AUTH_TOKEN" -ForegroundColor Red; return }

$env:ANTHROPIC_BASE_URL = "https://token-plan-cn.xiaomimimo.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN = $token
$env:ANTHROPIC_MODEL = "mimo-v2.5-pro[1m]"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "mimo-v2.5-pro[1m]"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "mimo-v2.5-pro[1m]"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "mimo-v2.5"
Remove-Item Env:CLAUDE_CODE_SUBAGENT_MODEL -ErrorAction SilentlyContinue
Remove-Item Env:CLAUDE_CODE_EFFORT_LEVEL -ErrorAction SilentlyContinue

Write-Host "已切换到 MiMo V2.5 Pro [1M] 环境" -ForegroundColor Cyan

# 切换到 DeepSeek V4 环境
# 用法：. .\tools\switch-deepseek.ps1 然后执行 claude
# API Key 从 .env 读取

$envFile = Join-Path $PSScriptRoot "..\.env"
$token = ""
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*DEEPSEEK_AUTH_TOKEN\s*=\s*(.+?)\s*$') { $token = $Matches[1] }
    }
}
if (-not $token -or $token -match "^<") { Write-Host "请在 .env 中填写 DEEPSEEK_AUTH_TOKEN" -ForegroundColor Red; return }

$env:ANTHROPIC_BASE_URL = "https://api.deepseek.com/anthropic"
$env:ANTHROPIC_AUTH_TOKEN = $token
$env:ANTHROPIC_MODEL = "deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_OPUS_MODEL = "deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_SONNET_MODEL = "deepseek-v4-pro[1m]"
$env:ANTHROPIC_DEFAULT_HAIKU_MODEL = "deepseek-v4-flash[1m]"
$env:CLAUDE_CODE_SUBAGENT_MODEL = "deepseek-v4-flash[1m]"
$env:CLAUDE_CODE_EFFORT_LEVEL = "max"

Write-Host "已切换到 DeepSeek V4 Pro [1M] 环境" -ForegroundColor Yellow

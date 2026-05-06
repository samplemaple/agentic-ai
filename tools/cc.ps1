# Claude Code 启动器 — 选择模型环境
# 用法：.\tools\cc.ps1
# API Key 从项目根目录 .env 文件读取
# 会自动更新 ~/.claude/settings.json 以确保配置生效

param(
    [string]$Model
)

# 读取 .env 文件
$envFile = Join-Path $PSScriptRoot "..\.env"
$envVars = @{}
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+?)\s*=\s*(.+?)\s*$') {
            $envVars[$Matches[1]] = $Matches[2]
        }
    }
} else {
    Write-Host ".env 文件不存在，请先复制 .env.example 为 .env 并填写 API Key" -ForegroundColor Red
    exit 1
}

$mimoToken = $envVars["MIMO_AUTH_TOKEN"]
$deepseekToken = $envVars["DEEPSEEK_AUTH_TOKEN"]

$models = @{
    "1" = @{
        Name   = "MiMo V2.5 Pro [1M]"
        Color  = "Cyan"
        Token  = $mimoToken
        Env    = [ordered]@{
            ANTHROPIC_BASE_URL              = "https://token-plan-cn.xiaomimimo.com/anthropic"
            ANTHROPIC_MODEL                 = "mimo-v2.5-pro[1m]"
            ANTHROPIC_DEFAULT_OPUS_MODEL    = "mimo-v2.5-pro[1m]"
            ANTHROPIC_DEFAULT_SONNET_MODEL  = "mimo-v2.5-pro[1m]"
            ANTHROPIC_DEFAULT_HAIKU_MODEL   = "mimo-v2.5"
        }
    }
    "2" = @{
        Name   = "DeepSeek V4 Pro [1M]"
        Color  = "Yellow"
        Token  = $deepseekToken
        Env    = [ordered]@{
            ANTHROPIC_BASE_URL              = "https://api.deepseek.com/anthropic"
            ANTHROPIC_MODEL                 = "deepseek-v4-pro[1m]"
            ANTHROPIC_DEFAULT_OPUS_MODEL    = "deepseek-v4-pro[1m]"
            ANTHROPIC_DEFAULT_SONNET_MODEL  = "deepseek-v4-pro[1m]"
            ANTHROPIC_DEFAULT_HAIKU_MODEL   = "deepseek-v4-flash[1m]"
            CLAUDE_CODE_SUBAGENT_MODEL      = "deepseek-v4-flash[1m]"
            CLAUDE_CODE_EFFORT_LEVEL        = "max"
        }
    }
}

# 显示菜单
if (-not $Model) {
    Write-Host ""
    Write-Host "=== Claude Code 模型选择 ===" -ForegroundColor White
    Write-Host ""
    Write-Host "  [1] MiMo V2.5 Pro [1M]" -ForegroundColor Cyan
    Write-Host "  [2] DeepSeek V4 Pro [1M]" -ForegroundColor Yellow
    Write-Host ""
    $Model = Read-Host "选择模型 (1/2)"
}

if (-not $models.ContainsKey($Model)) {
    Write-Host "无效选择: $Model，请输入 1 或 2" -ForegroundColor Red
    exit 1
}

$selected = $models[$Model]

# 检查 Token
if (-not $selected.Token -or $selected.Token -match "^<") {
    Write-Host "API Key 未配置，请在 .env 中填写对应的 Token" -ForegroundColor Red
    exit 1
}

# 构建 settings.json 的 env 对象
$settingsEnv = [ordered]@{
    ANTHROPIC_AUTH_TOKEN = $selected.Token
}
foreach ($kv in $selected.Env.GetEnumerator()) {
    $settingsEnv[$kv.Key] = $kv.Value
}

# 写入 ~/.claude/settings.json
$settingsPath = Join-Path $env:USERPROFILE ".claude\settings.json"
$settingsDir = Split-Path $settingsPath -Parent
if (-not (Test-Path $settingsDir)) {
    New-Item -ItemType Directory -Path $settingsDir -Force | Out-Null
}

$settingsObj = @{ env = $settingsEnv }
$settingsObj | ConvertTo-Json -Depth 10 | Set-Content -Path $settingsPath -Encoding UTF8

# 同时设置进程环境变量（双保险）
$env:ANTHROPIC_AUTH_TOKEN = $selected.Token
foreach ($kv in $selected.Env.GetEnumerator()) {
    [System.Environment]::SetEnvironmentVariable($kv.Key, $kv.Value, "Process")
}

Write-Host ""
Write-Host "已选择: $($selected.Name)" -ForegroundColor $selected.Color
Write-Host "settings.json 已更新" -ForegroundColor DarkGray
Write-Host "启动 Claude Code..." -ForegroundColor Green
Write-Host ""

# 启动 claude
claude

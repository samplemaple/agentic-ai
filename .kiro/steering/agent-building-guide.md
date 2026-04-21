---
inclusion: manual
---

# OpenClaw Agent 构建经验指南

基于晨间执行官（morning agent）项目的实战经验总结。

## Token 优化（最重要）

Token 消耗的三大来源：Tool schemas > Skills list > Bootstrap 文件。优化优先级按此排序。

### 1. 限制工具范围（效果最大，可省 50-80%）
- 每个 cron job 用 `--tools` 参数只加载必要工具（如 `--tools read,write,fetch`）
- 在 agents.list 中为子 Agent 配置 `tools.allow`，防止全局工具污染
- `tools.alsoAllow` 只保留真正需要的 MCP 工具，每个工具 schema 约 300-500 tokens
- 投递类 job 只需 `--tools read`

### 2. 限制 Skills（可省 ~3,000 tok）
- 用 `agents.list[].skills` 为每个 Agent 设置 skills allowlist
- 不需要 skills 的 Agent 设为空数组 `skills: []`
- 插件安装的 skills（如飞书、企微）即使插件 disabled，skills 仍会加载，必须通过 allowlist 排除

```json
{
  "agents": {
    "list": [
      { "id": "main", "skills": ["weather", "healthcheck"] },
      { "id": "morning", "skills": [], "tools": { "allow": ["read", "write", "fetch", "search"] } }
    ]
  }
}
```

### 3. 精简 SOUL.md（可省 10-20%）
- 控制在 50 行以内
- 定时任务的详细流程写在 cron message 里，不写在 SOUL.md

### 4. 其他优化
- cron job 加 `--light-context` 减少平台系统 prompt 开销
- 简单任务用 deepseek-chat + `--thinking off`，复杂任务才用 reasoner
- 长对话用 `/compact` 压缩历史
- 用 `/context list` 和 `/context detail` 诊断 token 构成

### 实测效果

| 场景 | 优化前 | 优化后 |
|------|--------|--------|
| 定时任务（晨间简报） | ~30,000 tok | ~4,500 tok |
| 日常对话（简单问答） | ~65,000 tok | ~131 tok（有缓存） |
| 系统 prompt 固定开销 | ~10,108 tok | ~7,406 tok |

## 子 Agent 微信投递问题

OpenClaw 2026.4.15 的限制：
- 子 Agent 无法直接投递到 main 绑定的微信渠道
- `agents bind` 会抢走 main 的消息入口（双向绑定）
- `sessions_spawn` 返回结果会被系统 NO_REPLY 拦截
- 不支持 `--deliver-to`、`outboundChannels`、`inheritChannelFrom`

**解决方案（文件中转）**：
- 子 Agent cron job 生成内容写入 /tmp 文件，`--no-deliver`
- main Agent 延后 5 分钟的 cron job 读取文件并投递，`--tools read`
- 正常对话仍走 sessions_spawn，不受影响

## Cron Job 配置模板

```bash
# 生成 job（子 Agent 执行，不投递）
openclaw cron add \
  --name "任务名" \
  --agent <子agent-id> \
  --cron "0 6 * * *" \
  --tz Asia/Shanghai \
  --no-deliver \
  --light-context \
  --tools read,write,fetch \
  --model custom-api-deepseek-com/deepseek-chat \
  --message "具体任务描述...最后写入 /tmp/output.txt"

# 投递 job（main 读取并发送）
openclaw cron add \
  --name "任务名投递" \
  --agent main \
  --cron "5 6 * * *" \
  --tz Asia/Shanghai \
  --channel openclaw-weixin \
  --announce \
  --light-context \
  --tools read \
  --model custom-api-deepseek-com/deepseek-chat \
  --thinking off \
  --message "读取 /tmp/output.txt 的内容，原样发出"
```

## SOUL.md 编写原则

- 身份定位 + 数据文件路径 + 核心规则，控制在 50 行
- 详细流程写在 cron message 里，不写在 SOUL.md
- 安全边界必须保留（禁止访问内网、禁止输出凭证）
- 格式模板用简短描述，不要写完整示例

## 项目文件结构

```
openclaw-<project>/
├── README.md              # 项目说明
├── session-context.md     # 当前进度快照（steering auto inclusion）
└── deploy/
    ├── agents/<id>/SOUL.md  # Agent 人格文件
    └── <project>/           # 数据文件（config、日历等）
```

## 部署命令

```bash
# 部署 SOUL.md
scp deploy/agents/<id>/SOUL.md root@<server>:~/.openclaw/agents/<id>/SOUL.md

# 部署数据文件
scp deploy/<project>/* root@<server>:/root/<project>/

# 验证
ssh root@<server> "openclaw cron list"
ssh root@<server> "openclaw cron run <job-id>"
ssh root@<server> "openclaw cron runs --id <job-id> --limit 1"
```

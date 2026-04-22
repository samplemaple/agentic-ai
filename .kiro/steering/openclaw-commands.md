---
inclusion: auto
description: OpenClaw CLI 命令速查，包含 cron 定时任务管理、Agent 管理、文件部署和服务管理等常用命令
---

# OpenClaw CLI 命令速查

## Cron 定时任务管理

### 查看定时任务
```bash
openclaw cron list                    # 列出所有定时任务
openclaw cron list --json             # JSON 格式输出
openclaw cron list --json | jq '.jobs[] | {name, id, agentId, delivery}'
```

### 编辑定时任务
```bash
openclaw cron edit <job-id> [options]
```

常用参数：
| 参数 | 说明 |
|------|------|
| `--message <text>` | 设置任务的 prompt 消息内容（不是 --prompt） |
| `--agent <id>` | 设置执行 Agent |
| `--cron <expr>` | 设置 cron 表达式 |
| `--tz <timezone>` | 设置时区（IANA 格式） |
| `--model <model>` | 模型覆盖 |
| `--timeout-seconds <n>` | Agent 任务超时秒数 |
| `--channel <channel>` | 投递渠道（last 或具体渠道名） |
| `--announce` | 启用 announce 投递到聊天 |
| `--no-deliver` | 禁用 announce 投递 |
| `--expect-final` | 等待 Agent 最终回复 |
| `--light-context` | 启用轻量上下文（减少 ctx 占用） |
| `--enable` / `--disable` | 启用/禁用任务 |
| `--name <name>` | 设置任务名称 |
| `--description <desc>` | 设置任务描述 |
| `--session <mode>` | 会话模式（main 或 isolated） |
| `--thinking <level>` | 思考级别（off/minimal/low/medium/high/xhigh） |

### 当前定时任务 ID

| 任务 | ID | Agent | 时间 |
|------|-----|-------|------|
| 晨间简报（生成） | `7506dd61-0135-4f1f-9f6f-a0daadbb9643` | morning | 每天 6:00 |
| 晨间简报投递 | `41206a6a-7ea8-464d-8272-e2b1e77c9bd2` | main | 每天 6:05 |
| 晚间简报（生成） | `c7176611-6980-4528-a067-0f815f99b413` | morning | 每天 19:00 |
| 晚间简报投递 | `434a5e43-10dd-4b0e-865e-4470c0538b60` | main | 每天 19:05 |
| 公众号文章生成 | `dd1b9916-b139-4d49-bdde-a617b18d0db8` | wechat-writer | 每天 8:00 |
| 公众号文章邮件发送 | `a29157e8-0497-42bf-b4a3-d1fa2df19150` | main | 每天 8:10 |

## 文件部署到服务器

使用 `cat > <服务器路径> << 'EOF'` 方式写入，无需重启 openclaw 服务。
SOUL.md 和数据文件在下次任务触发时自动生效。

morning Agent 的 SOUL.md 在服务器上有两份，更新后需要同步：
```bash
# 写入主文件后，复制到第二个位置
cp ~/.openclaw/workspace/morning/SOUL.md ~/.openclaw/agents/morning/SOUL.md
```

## Agent 管理

```bash
openclaw agents list                  # 列出所有 Agent
openclaw agents bind --agent <id> --bind "<channel>"    # 绑定渠道（注意：会影响消息路由）
openclaw agents unbind --agent <id> --bind "<channel>"  # 解绑渠道
```

## 服务管理

```bash
sudo systemctl restart openclaw       # 重启服务（一般不需要）
sudo systemctl status openclaw        # 查看服务状态
journalctl -u openclaw -f             # 实时日志
journalctl -u openclaw --since '1 hour ago'  # 最近 1 小时日志
```

---
inclusion: auto
description: OpenClaw CLI 命令速查，覆盖会话管理、Channel 管理、插件管理、服务管理、配置管理、Agent 管理等常用命令
---

# OpenClaw CLI 命令速查

## 会话管理（上下文查看）

等效于旧的 `/context list`：

```bash
openclaw sessions                        # 列出所有会话（含 token 消耗）
openclaw sessions --active 120           # 最近 2 小时活跃会话
openclaw sessions --json                 # JSON 格式，包含更多细节
openclaw sessions --limit 25             # 最近 25 条
openclaw sessions --agent main           # 查看指定 agent 的会话
```

Token 消耗显示在 `Tokens (ctx %)` 列。设置 `agents.defaults.contextTokens` 可调整上下文窗口上限。

## Channel 管理

```bash
openclaw channels status --probe         # 所有 Channel 连接状态（含健康检查）
openclaw channels login --channel feishu # 扫码绑定飞书（交互式）
openclaw channels add --channel feishu --app-token <token> --secret <secret>  # 手动添加
openclaw config get channels.feishu      # 查看飞书 Channel 配置
```

### 配对管理（DM 审批）

```bash
openclaw pairing list feishu             # 查看飞书待审批配对
openclaw pairing approve feishu <码>     # 批准配对
```

### DM / 群聊策略

```bash
openclaw config set channels.feishu.dmPolicy open      # 所有用户可直接私聊
openclaw config set channels.feishu.dmPolicy pairing   # 新用户需配对审批（默认）
openclaw config set channels.feishu.dmPolicy allowlist # 仅白名单用户可私聊
openclaw config set channels.feishu.requireMention false --json  # 群聊无需 @ 也回复
```

## 插件管理

```bash
openclaw plugins list                                     # 列出所有插件（含启用状态）
openclaw plugins install <包名> --dangerously-force-unsafe-install  # 安装插件
openclaw config set plugins.entries.<plugin-id>.enabled false --json  # 禁用插件
openclaw config set plugins.entries.<plugin-id>.enabled true --json   # 启用插件
```

当前安装的飞书插件：
- `@larksuite/openclaw-lark` — 飞书官方插件（日历/文档/多维表格/知识库等工具）

## 配置管理

```bash
openclaw config get <path>               # 读取配置项（如 channels.feishu）
openclaw config set <path> <value>       # 设置配置项（字符串值）
openclaw config set <path> <value> --json  # 设置 JSON 值（布尔/对象）
openclaw config validate                 # 验证配置文件
openclaw configure                       # 交互式配置向导
```

配置文件位置：`~/.openclaw/openclaw.json`

## 服务管理

```bash
sudo systemctl restart openclaw          # 重启 Gateway（改配置后必须重启）
sudo systemctl status openclaw           # 查看服务状态
journalctl -u openclaw -f                # 实时日志
journalctl -u openclaw --since '10 min ago'  # 最近 10 分钟日志
journalctl -u openclaw --since '1 hour ago' | grep feishu  # 过滤飞书相关日志
openclaw health                          # Gateway 健康检查
openclaw logs                            # 通过 RPC 查看文件日志
```

## Agent 管理

```bash
openclaw agents list                     # 列出所有 Agent（含路由规则）
openclaw agents create --name <id>       # 创建新 Agent
```

## Cron 定时任务

```bash
openclaw cron list                       # 列出所有定时任务
openclaw cron list --json                # JSON 格式
openclaw cron edit <job-id> --enable     # 启用任务
openclaw cron edit <job-id> --disable    # 禁用任务
openclaw cron edit <job-id> --message "新 prompt"  # 修改任务消息
```

## 文件部署到服务器

```bash
# SOUL.md / AGENTS.md 部署
scp <本地文件> root@<tailscale域名>:~/.openclaw/workspace/<agent>/SOUL.md

# 或直接写入（无需重启，下次对话自动生效）
cat > /root/.openclaw/workspace/SOUL.md << 'EOF'
...内容...
EOF
```

修改 SOUL.md / AGENTS.md 不需要重启服务，下次 Agent 会话自动加载。

## 模型管理

```bash
openclaw models list                     # 查看已配置模型
openclaw models scan                     # 扫描可用模型
```

## 安全审计

```bash
openclaw security audit --deep           # 深度安全扫描（含插件代码模式）
openclaw doctor                          # 健康检查 + 快速修复
```

## 常用快捷操作

```bash
# 改完配置后的标准重启流程
sudo systemctl restart openclaw && sleep 3 && openclaw channels status --probe

# 查飞书是否有新用户请求配对
openclaw pairing list feishu

# 实时监控飞书日志
journalctl -u openclaw -f | grep -i feishu
```

# Agent 自动化安全加固清单

> 在实现晨间执行官、SEO 流水线、Agent 军团等自动化场景前，必须逐项检查
> 本清单是 [security-checklist.md](security-checklist.md) 的补充，专门针对 Agent 自动化场景

---

## 零、前置：基础设施安全（必须先完成）

在开始任何 Agent 自动化之前，确保已通过 [基础安全检查清单](security-checklist.md) 的全部项目：

- [ ] Gateway 绑定 127.0.0.1（`gateway.mode local`）
- [ ] Tailscale 已配置并认证
- [ ] 云服务器安全组关闭所有入站端口
- [ ] systemd 守护进程已配置

> ⚠️ 如果基础设施安全未通过，不要开始配置 Agent 自动化。13.5 万个 OpenClaw 实例因端口暴露被攻击的教训就在眼前。

---

## 一、🔴 凭证安全（最高优先级）

Agent 自动化涉及多个外部服务的 API Key，任何一个泄露都可能造成经济损失。

### 1.1 API Key 管理

- [ ] 所有 API Key 存放在 `/opt/openclaw.env` 中，权限 600
- [ ] `~/.openclaw/openclaw.json` 中的 apiKey 字段不包含真实 Key（使用环境变量引用）
- [ ] `.gitignore` 中已包含以下条目：

```
openclaw.json
.env
*.env
openclaw.env
```

- [ ] 已确认 Git 历史中没有提交过 API Key（如有，立即轮换）

**验证命令：**
```bash
# 检查 .env 文件权限
ls -la /opt/openclaw.env
# 应显示 -rw------- (600)

# 检查 Git 历史中是否有 Key 泄露
git log --all -p | grep -i "apikey\|api_key\|secret\|password" | head -20
```

### 1.2 WordPress 应用密码

- [ ] 使用 WordPress「应用密码」而非登录密码
- [ ] 应用密码仅授予必要权限（发布文章）
- [ ] 定期轮换（建议每 90 天）

### 1.3 企微 Bot 凭证

- [ ] Bot ID 和 Secret 存放在配置文件中，不硬编码在脚本里
- [ ] 如怀疑泄露，立即在企微管理后台重新生成

---

## 二、🔴 MCP 工具权限控制

MCP 工具是 Agent 的"手"——权限过大等于给 Agent 一把万能钥匙。

### 2.1 文件系统 MCP

- [ ] filesystem MCP 的路径限制在最小必要范围

```json
// ✅ 正确：只开放特定目录
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/root/seo-pipeline"]

// ❌ 错误：开放整个根目录
"args": ["-y", "@modelcontextprotocol/server-filesystem", "/"]
```

- [ ] 不同 Agent 使用不同的 filesystem 路径，互相隔离
- [ ] 敏感目录（`/opt`、`/etc`、`~/.ssh`）绝不暴露给 MCP

### 2.2 Puppeteer MCP

- [ ] 设置为 headless 模式（`PUPPETEER_HEADLESS: "true"`）
- [ ] 在 SOUL.md 中明确禁止访问非竞品网站
- [ ] 在 SOUL.md 中要求遵守 robots.txt

### 2.3 fetch MCP

- [ ] 在 SOUL.md 中限制 fetch 的目标域名范围
- [ ] 禁止 Agent 通过 fetch 访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x）
- [ ] 禁止 Agent 通过 fetch 访问云厂商元数据接口（169.254.169.254）

### 2.4 Shell 执行（如有）

- [ ] 仅运维 Agent 有 Shell 执行权限，其他 Agent 禁用
- [ ] 在 SOUL.md 中明确禁止的命令：`rm -rf`、`dd`、`mkfs`、`shutdown`、`reboot`
- [ ] 在 SOUL.md 中限制可执行的命令白名单

---

## 三、🟡 SOUL.md 安全边界

SOUL.md 是 Agent 行为的"宪法"，必须包含安全约束。

### 3.1 通用安全规则（所有 Agent 必须包含）

在每个 Agent 的 SOUL.md 中添加：

```markdown
## 安全边界（不可违反）

### 禁止操作
- 不得删除、修改或覆盖系统文件
- 不得访问 /etc、/opt、~/.ssh 等敏感目录
- 不得执行任何涉及 rm -rf、dd、mkfs 的命令
- 不得将 API Key、密码、Token 等凭证输出到消息中
- 不得访问内网地址（127.0.0.1、10.x.x.x、192.168.x.x、169.254.x.x）
- 不得在未经确认的情况下发布内容到公开平台

### 数据安全
- 所有数据仅在本服务器处理，不得传输到第三方
- 不得在日志或消息中暴露用户的个人信息
- 遇到不确定的操作，先存为草稿/暂停，通知用户确认
```

- [ ] 所有 Agent 的 SOUL.md 都包含上述安全边界
- [ ] 定期审查 SOUL.md，确保安全规则未被意外修改

### 3.2 场景特定安全规则

| 场景 | 额外安全规则 |
|------|------------|
| SEO 流水线 | 初期 publishStatus 设为 draft；遵守 robots.txt；不攻击竞品 |
| 晨间简报 | 不在简报中暴露敏感提醒内容（如合同金额） |
| Agent 军团 | 路由 Agent 不直接执行任务，只做分发；各 Agent 权限最小化 |

---

## 四、🟡 Heartbeat 安全控制

Heartbeat 让 Agent 自主运行，失控风险最高。

### 4.1 频率限制

- [ ] 定时任务频率合理（晨间简报每天 1 次，SEO 每天 2-4 次）
- [ ] 不设置每分钟级别的 Heartbeat（会快速消耗 Token 并可能触发 API 限流）

### 4.2 Token 预算

- [ ] 配置 `maxTokensPerDay` 防止 Token 消耗失控

```json
{
    "agents": {
        "defaults": {
            "maxTokensPerDay": 500000
        }
    }
}
```

- [ ] 定期检查火山引擎/Hotai 的用量面板，确认消耗在预期范围内

### 4.3 失败处理

- [ ] 在 SOUL.md 中要求：如果某个步骤失败，跳过并通知用户，不要无限重试
- [ ] 监控 `journalctl -u openclaw -f` 日志，关注异常重复执行

### 4.4 紧急停止

如果 Agent 行为异常，立即执行：

```bash
# 方法 1：停止 OpenClaw 服务
sudo systemctl stop openclaw

# 方法 2：仅禁用 Heartbeat（不停止整个服务）
openclaw config set heartbeat.enabled false
sudo systemctl restart openclaw
```

- [ ] 已知道如何紧急停止 Agent

---

## 五、🔵 数据主权与隐私

根据图片中的架构，所有数据都在你自己的服务器上，但仍需注意：

### 5.1 数据存储

```
你的云服务器
├── ~/.openclaw/
│   ├── openclaw.json          ← 你的配置（含 API Key 引用）
│   └── agents/
│       ├── main/
│       │   ├── SOUL.md        ← 你的人格配置
│       │   ├── MEMORY.md      ← 你的记忆数据
│       │   └── sessions/      ← 你的会话记录
│       ├── seo/               ← SEO Agent 数据
│       └── morning/           ← 晨间 Agent 数据
├── /root/seo-pipeline/        ← SEO 流水线数据
├── /root/morning-briefing/    ← 晨间简报数据
└── /opt/openclaw.env          ← API Key（权限 600）
```

- [ ] 所有数据目录权限正确（仅 root 可读写）
- [ ] 定期备份 `~/.openclaw/` 目录
- [ ] 备份文件加密存储，不上传到公开云盘

### 5.2 模型调用隐私

- [ ] 了解你使用的模型提供商的数据政策：
  - 火山引擎：数据不用于训练（企业版）
  - Hotai 代理：数据经过第三方中转，敏感数据谨慎使用
- [ ] 涉及敏感业务数据的 Agent，优先使用国产模型（火山引擎直连）

---

## 六、🔵 网络安全加固

### 6.1 零公网 IP 架构验证

```
┌─────────────────────────────────────────────────┐
│  你的云服务器                                      │
│                                                   │
│  Tailscale (tailscale serve --bg 18789)          │
│       ↓                                           │
│  OpenClaw Gateway (127.0.0.1:18789)              │
│       ↑                                           │
│  systemd 守护进程                                  │
│                                                   │
│  防火墙：所有入站端口关闭                            │
│  公网 IP：无 / 不使用                               │
└─────────────────────────────────────────────────┘
```

- [ ] `ss -tlnp | grep 18789` 显示 `127.0.0.1:18789`（不是 `0.0.0.0`）
- [ ] 云服务器安全组：入站规则为空（所有端口关闭）
- [ ] Tailscale Serve 模式（非 Funnel）——仅 tailnet 内设备可访问

### 6.2 企微 Webhook 安全

如果使用企微长连接模式（推荐），无需公网 IP。但如果使用 Webhook 回调模式：

- [ ] 仅在必要时开启 Tailscale Funnel（`tailscale funnel --bg 18789`）
- [ ] Funnel 开启后，确认 Gateway Token 认证已配置
- [ ] 不需要时立即关闭 Funnel（`tailscale funnel 18789 off`）

---

## 七、审计与监控

### 7.1 日志审计

```bash
# 实时查看 Agent 操作日志
journalctl -u openclaw -f

# 查看最近 1 小时的日志
journalctl -u openclaw --since '1 hour ago'

# 搜索异常关键词
journalctl -u openclaw | grep -i "error\|failed\|denied\|unauthorized"
```

- [ ] 每周至少查看一次 Agent 日志
- [ ] 关注异常模式：频繁重试、未知 URL 访问、Token 消耗突增

### 7.2 成本监控

- [ ] 每周检查火山引擎 Coding Plan 用量
- [ ] 每周检查 Hotai 余额
- [ ] 设置 `maxTokensPerDay` 作为安全阀

---

## ✅ 完成确认

全部检查通过后，你的 Agent 自动化具备：

| 安全能力 | 状态 |
|---------|------|
| 零公网暴露 | ✅ Tailscale Serve + 127.0.0.1 绑定 |
| 凭证安全 | ✅ 环境变量注入 + 权限 600 + .gitignore |
| MCP 权限最小化 | ✅ 每个 Agent 仅开放必要的目录和工具 |
| SOUL.md 安全边界 | ✅ 所有 Agent 包含禁止操作清单 |
| Heartbeat 可控 | ✅ Token 预算 + 频率限制 + 紧急停止 |
| 数据主权 | ✅ 全部数据在自己服务器，定期备份 |
| 审计可追溯 | ✅ systemd 日志 + 定期审查 |

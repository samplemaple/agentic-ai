---
inclusion: manual
description: OpenClaw Agent 构建速查，包含 Token 优化规则、工具精简、配置变更生效方式和常见踩坑
---

# OpenClaw Agent 构建速查

> 详细踩坑记录和完整命令见 `openclaw-multi-agent/agent-building-guide.md`

---

## 一、Token 优化规则

消耗来源排序：Tool schemas > Skills list > AGENTS.md > SOUL.md > 对话历史

### 1. 工具白名单（效果最大）

每个 Agent 只加载需要的工具，每个工具 schema 约 165 tok。

| Agent | tools.allow | 说明 |
|-------|------------|------|
| main | read, edit, write, exec, process, message, web_fetch, memory_search, memory_get, agents_list, sessions_spawn, sessions_send, sessions_list, subagents（14 个） | 去掉 canvas/tts/image/pdf/qqbot_remind/wecom_mcpSession/sessions_history/sessions_yield/session_status |
| morning | read, write, fetch, search（4 个） | 极简，只做简报生成 |
| cron 投递 job | read（1 个） | 只需读 /tmp 文件 |

### 2. Skills 白名单

- main：`["weather", "healthcheck"]`
- 子 Agent：`[]`（空数组）
- 插件安装的 skills 即使插件 disabled 仍会加载，必须通过 allowlist 排除

### 3. AGENTS.md 裁剪

默认模板 ~1,951 tok，裁剪后 ~959 tok。去掉的内容：

- 群聊规则（微信 ClawBot 不支持群聊）
- Reactions（微信不支持）
- Voice Storytelling / TTS（未配置 ElevenLabs）
- Discord/WhatsApp 格式规则（只用微信）
- Heartbeat 详细检查项和 Memory Maintenance（用 cron 不用 heartbeat 巡逻）

### 4. SOUL.md 精简

- 控制在 50 行以内
- 详细流程写在 cron message 里，不写在 SOUL.md
- 安全边界必须保留

### 5. Cron Job 优化

- `--light-context` 减少系统 prompt 开销
- `--tools` 限制工具范围
- `--thinking off` 用于简单投递任务
- deepseek-chat 用于日常，deepseek-reasoner 用于复杂任务

### 实测数据

| 指标 | 优化前 | 优化后 |
|------|--------|--------|
| main 固定开销 | ~15,000 tok | ~12,300 tok |
| 定时任务（晨间简报） | ~30,000 tok/次 | ~4,500 tok/次 |
| AGENTS.md | 1,951 tok | 959 tok |
| Tool schemas | 3,798 tok（23 个） | 2,988 tok（14 个） |

---

## 二、配置变更生效方式

| 改了什么 | 怎么生效 |
|---------|---------|
| SOUL.md / AGENTS.md | 下次新会话自动生效 |
| openclaw.json 中 tools/skills | 需要新会话（`/reset` 或等 `/compact`） |
| openclaw.json 中 models | `rm ~/.openclaw/agents/main/agent/models.json` + `systemctl restart openclaw` |
| cron job 参数 | 立即生效，不需要重启 |
| HEARTBEAT.md | 下次心跳触发时生效 |

微信中触发新会话的方式：
- `/compact` — 压缩上下文（短时间内不能重复）
- `/reset` — 彻底重置，聊天记录清零
- `/context list` — 查看当前 token 构成

---

## 三、架构要点

- 所有 IM 渠道共享一个 main Agent 做路由，子 Agent 不直接对接 IM
- 微信渠道只绑定在 main 上，不要给子 Agent 绑定（会抢走消息入口）
- 图片生成、PDF 等能力按需给子 Agent 开，不放在 main 里
- `compaction.mode: safeguard` 自动压缩，压缩后仍可能占 50-55k/64k

---

## 四、定时任务投递方案

子 Agent 无法直接投递微信，使用文件中转：

```
6:00  morning Agent 生成简报 → 写入 /tmp/morning-report.txt（--no-deliver）
6:05  main Agent 读取 /tmp 文件 → 投递到微信（--tools read --announce）
```

不要用 sessions_spawn 做定时投递（会被系统 NO_REPLY 机制拦截）。
sessions_spawn 只适合用户实时对话时的路由。

---

## 五、DNS 与网络

- Tailscale MagicDNS 接管 /etc/resolv.conf，可能导致外部域名解析失败
- 在 Tailscale 后台 https://login.tailscale.com/admin/dns 添加全局 DNS：223.5.5.5 和 8.8.8.8
- 手动改 /etc/resolv.conf 会被 Tailscale 覆盖，后台配置更可靠

---

## 六、常见踩坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 100% context used | contextWindow 默认 16000 太小 | 改为 64000 |
| 修改 openclaw.json 不生效 | models.json 缓存优先级更高 | 删除 models.json + 重启 |
| 微信收不到定时任务 | 子 Agent 没有微信渠道 | 用文件中转方案 |
| agents bind 后消息全跑到子 Agent | 双向绑定抢走 main 入口 | unbind + 只保留 main 绑定 |
| auth.json 写入内容后控制台卡死 | 必须保持 `{}` 空对象 | 清空为 `{}` |
| 服务器 DNS 解析失败 | Tailscale MagicDNS 接管 | 后台添加全局 DNS |
| /compact 提示 skipped | 短时间内不能重复压缩 | 等一会或用 /reset |

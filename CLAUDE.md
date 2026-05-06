# CLAUDE.md

本文件指导 Claude Code 在此仓库中的工作方式。

## 语言规则

所有回答、解释、代码注释、文档撰写、PR 描述等，均**必须使用中文**。术语、代码、命令、文件路径等固有英文内容保留原文。

## 仓库定位

OpenClaw + Claude Code 生产部署指南与《AI 业务流架构师》课程配套资料。涵盖 OpenClaw 部署、飞书 IM 接入、Agent 人格工程（SOUL.md）、心跳自动化、模型配置及变现方案。

## 当前项目状态

- **OpenClaw v2026.5.5** 运行于火山引擎 Ubuntu 22.04，Tailscale 安全穿透
- **飞书 IM** 已接入，WebSocket 模式，`@larksuite/openclaw-lark` 插件
- **待完成**：Agent 人格配置（SOUL.md + AGENTS.md）、Heartbeat 定时任务
- 实时状态见 `project-session.md`

## 目录结构

```
openclaw-infra/              # 基础设施：一键部署、systemd、Tailscale 安全穿透、安全清单
openclaw-im/                 # IM 渠道接入：飞书原生集成、微信 ClawBot（未启用）、企微（未启用）
openclaw-models/             # 模型配置：DeepSeek、火山引擎 Coding Plan、Hotai 海外模型
openclaw-soul/               # 人格工程：SOUL.md 四层建造法 + AGENTS.md 权限矩阵
openclaw-heartbeat/          # 心跳引擎：Cron vs Heartbeat 选型、HEARTBEAT.md 设计方法论
openclaw-morning-briefing/   # 晨间/晚间简报系统（参考模板）
openclaw-cs-agent/           # 智能客服 Agent（变现方向 A，待开发）
tools/                       # Claude Code 模型环境切换脚本（PowerShell）
.kiro/steering/              # Claude Code 自动加载的参考文件
```

## 核心架构概念

- **SOUL.md 四层建造法**: Identity → Communication Style → Values & Rules → Boundaries
- **AGENTS.md 三级权限**: Act & Report / Propose First / Critical
- **Heartbeat 四条黄金法则**: 精简至上、阈值明确、必须有停止条件、设定时段窗口
- **Cron vs Heartbeat 选型**: 心跳看状态，Cron 干活；组合使用是生产最常见模式
- **安全三原则**: 永不提交 `.env` 到 Git、永不绑定端口到 `0.0.0.0`、永不开放 18789 端口

## 常用命令

### 服务器连接（SSH + Tailscale）
- `ssh -i "C:\Users\Administrator\Desktop\LocalPem\Yang260418.pem" root@iv-yekai6mkn4sobos7uo0f-1.tailc81ecf.ts.net`
- 完整命令速查见 `.kiro/steering/openclaw-commands.md`（Claude 自动加载）

### 环境切换
- `.\tools\cc.ps1` — 交互式模型选择器
- `. .\tools\switch-deepseek.ps1` — 切换到 DeepSeek V4 环境
- API Key 存放在项目根目录 `.env` 文件

### OpenClaw 关键操作
- `openclaw sessions --active 120` — 查看会话上下文消耗（替代旧的 /context list）
- `openclaw channels status --probe` — Channel 连接健康检查
- `openclaw plugins list` — 查看所有插件状态
- `sudo systemctl restart openclaw` — 改配置后重启 Gateway

## 重要文件

- `project-session.md` — 中央状态快照（服务器信息、完成/待办事项）
- `openclaw.json.example` — OpenClaw 完整配置模板
- `.env` — API Key + 飞书凭据（已 gitignore，禁止提交）
- `.kiro/steering/openclaw-commands.md` — CLI 命令速查（Claude 自动加载）

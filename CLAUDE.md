# CLAUDE.md

本文件指导 Claude Code 在此仓库中的工作方式。

## 语言规则

所有回答、解释、代码注释、文档撰写、PR 描述等，均**必须使用中文**。术语、代码、命令、文件路径等固有英文内容保留原文。

## 仓库定位

OpenClaw + Claude Code 生产部署指南与《AI 业务流架构师》课程配套资料。涵盖 OpenClaw 部署、IM 接入（微信/企微/飞书）、Agent 人格工程（SOUL.md）、心跳自动化、模型配置及变现方案。

## 目录结构

```
openclaw-infra/              # 基础设施：一键部署、systemd、Tailscale 安全穿透、安全清单
openclaw-im/                 # IM 渠道接入：微信 ClawBot、企微、飞书
openclaw-models/             # 模型配置：DeepSeek、火山引擎 Coding Plan、Hotai 海外模型
openclaw-soul/               # 人格工程：SOUL.md 四层建造法 + AGENTS.md 权限矩阵
openclaw-heartbeat/          # 心跳引擎：Cron vs Heartbeat 选型、HEARTBEAT.md 设计方法论
openclaw-morning-briefing/   # 晨间/晚间简报系统（已部署运行）
openclaw-cs-agent/           # 智能客服 Agent（变现方向 A）
tools/                       # Claude Code 模型环境切换脚本（PowerShell）
```

## 核心架构概念

- **SOUL.md 四层建造法**: Identity → Communication Style → Values & Rules → Boundaries
- **AGENTS.md 三级权限**: Act & Report / Propose First / Critical
- **Heartbeat 四条黄金法则**: 精简至上、阈值明确、必须有停止条件、设定时段窗口
- **Cron vs Heartbeat 选型**: 心跳看状态，Cron 干活；组合使用是生产最常见模式
- **安全三原则**: 永不提交 `.env` 到 Git、永不绑定端口到 `0.0.0.0`、永不开放 18789 端口

## 常用命令

### 环境切换
- `.\tools\cc.ps1` — 交互式模型选择器（MiMo / DeepSeek V4）
- `. .\tools\switch-deepseek.ps1` — 切换到 DeepSeek V4 环境
- `. .\tools\switch-mimo.ps1` — 切换到 MiMo 环境
- API Key 存放在项目根目录 `.env` 文件

### 服务器部署（SSH + Tailscale）
- `ssh root@100.69.216.12` — 连接生产服务器
- `ssh -L 18789:127.0.0.1:18789 root@100.69.216.12` — 端口转发打开 OpenClaw 控制台
- `scp <本地文件> root@100.69.216.12:~/.openclaw/workspace/<agent>/SOUL.md` — 部署 SOUL.md
- SOUL.md 同步：`scp` 上传后需 `cp` 从 workspace 同步到 agents 目录

### OpenClaw 管理
- `openclaw cron list` — 查看所有定时任务
- `openclaw cron edit <id> --enable/--disable` — 启用/禁用定时任务
- `openclaw gateway token` — 管理 Gateway 访问令牌

### Session Context
- `session-context.md` — 中央状态快照（服务器信息、Agent 列表、定时任务、成本、路线图）
- `openclaw-commands.md` — CLI 命令速查（Claude 自动加载）
- `agent-building-guide.md` — Token 优化、工具精简、配置技巧（需手动引用）
- `server-deploy.md` — 连接详情、路径映射、Tailscale 网络（需手动引用）

## 重要文件

- `openclaw.json.example` — OpenClaw 完整配置模板
- `.env` — API Key（已 gitignore，禁止提交）
- `session-context.md` — 项目状态快照（服务器信息、Agent 列表、定时任务、成本估算、变现路线图）

## 变现方向

- **方向 A（推进中）**: 企业智能客服 Agent — RAG + 多轮对话 + 工具调用 + 转人工
- **方向 B（已暂停）**: 内容运营 Agent — 热点感知、选题规划、内容质检、效果闭环
- **方向 C（已暂停）**: 个人效率 Agent — 邮件摘要、GitHub/RSS 监控、日程协调

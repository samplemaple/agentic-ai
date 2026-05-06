# Project Session — OpenClaw 部署与配置

最后更新：2026-05-06 22:30

---

## 状态总览

| 模块 | 状态 |
|------|------|
| OpenClaw Gateway | v2026.5.5，systemd 运行中，端口 18789 |
| 网络与安全 | Tailscale 穿透，公网 22 关闭，Token 认证已启用 |
| 模型 | DeepSeek V4 Flash (1M ctx, 默认) + DeepSeek V4 Pro (1M ctx) |
| 飞书 IM | WebSocket 模式，`@larksuite/openclaw-lark` 插件，DM + 群聊正常 |
| Agent 人格 | 待配置（SOUL.md + AGENTS.md） |
| 定时任务 | 待配置 |
| ClawHub | 已登录 `@samplemaple` |

---

## 服务器信息

| 项目 | 值 |
|------|-----|
| 云厂商 / OS | 火山引擎 · Ubuntu 22.04.4 LTS |
| 公网 IP | 101.47.152.111（22 端口已关） |
| Tailscale 域名 | iv-yekai6mkn4sobos7uo0f-1.tailc81ecf.ts.net |
| SSH 密钥 | `C:\Users\Administrator\Desktop\LocalPem\Yang260418.pem` |
| Dashboard | `https://iv-yekai6mkn4sobos7uo0f-1.tailc81ecf.ts.net/#token=2ebe113fdf1857c3a6659f0fe9bfcab8d6d6e377cb519fe0` |

## 本地环境

| 项目 | 值 |
|------|-----|
| 项目路径 | `D:\AIStudy\agentic-ai` |
| SSH 密钥 | `C:\Users\Administrator\Desktop\LocalPem\Yang260418.pem` |

---

## 待完成

### 优先级高
- [ ] **配置主 Agent（SOUL.md + AGENTS.md）** — 参考 `openclaw-soul/`
- [ ] **配置定时任务（Heartbeat）** — 参考 `openclaw-heartbeat/`

### 优先级中
- [ ] **安装 ClawHub Skills** — `openclaw skills install <技能名>`
- [ ] **智能客服 Agent（变现方向 A）** — 参考 `openclaw-cs-agent/`

### 优先级低 / 可选
- [ ] **火山引擎 Coding Plan** — `openclaw-models/volcengine-coding-plan.md`
- [ ] **Hotai 海外模型代理** — `openclaw-models/hotai-api.md`
- [ ] **安全加固复查** — `openclaw-infra/checklists/security-checklist.md`

---
inclusion: manual
---

# 服务器部署信息

## 连接方式

- 工具：Tabby（SSH 终端）
- 服务器地址：见 `openclaw-morning-briefing/.env` 中的 `SERVER_HOST`
- 用户名：root
- 密码：见 `openclaw-morning-briefing/.env` 中的 `SERVER_PASSWORD`
- 网络：Tailscale 私有网络，零公网暴露

## 部署路径映射

| 本地文件 | 服务器路径 |
|---------|-----------|
| `deploy/morning-briefing/*` | `/root/morning-briefing/` |
| `deploy/agents/main/SOUL.md` | `~/.openclaw/agents/main/SOUL.md` |
| `deploy/agents/morning/SOUL.md` | `~/.openclaw/agents/morning/SOUL.md` |
| `deploy/openclaw.json` | 合并到 `~/.openclaw/openclaw.json` |

## 部署方式

- main（路由 Agent）：通过 OpenClaw 控制台界面配置
- morning（晨间执行官）：通过 Tabby SSH 到服务器部署文件

---
inclusion: manual
description: 服务器部署信息，包含连接方式、Tailscale 网络、路径映射和运维信息
---

# 服务器部署信息

## Tailscale 网络

| 设备 | Tailscale IP | 状态 |
|------|-------------|------|
| 服务器（iv-yekai6mkn4sobos7uo0f） | 100.69.216.12 | ✅ 在线 |
| 新电脑（desktop-3ed7f4o） | 100.122.156.13 | ✅ 在线 |
| 旧电脑（pc-202508171556） | 100.103.226.95 | 离线 |

管理后台：https://login.tailscale.com/admin/machines

## 连接方式

```bash
# SSH 连接（通过 Tailscale IP）
ssh root@100.69.216.12

# 访问 OpenClaw 控制台（SSH 端口转发）
ssh -L 18789:127.0.0.1:18789 root@100.69.216.12
# 然后浏览器打开 http://localhost:18789

# 或直接通过 Tailscale Serve
# 浏览器打开 https://<服务器>.ts.net/
```

Windows 上 Tailscale CLI 路径：`C:\Program Files\Tailscale\tailscale.exe`

## 服务器信息

- OpenClaw 版本：2026.4.15
- 系统：Ubuntu（Linux）
- 公网 22 端口已关闭，只能通过 Tailscale 访问
- DNS：Tailscale MagicDNS + 全局 fallback（223.5.5.5, 8.8.8.8）

## 部署路径映射

| 本地文件 | 服务器路径 |
|---------|-----------|
## 部署路径映射

| 本地路径 | 服务器路径 |
|---------|-----------|
| `openclaw-morning-briefing/deploy/morning-briefing/*` | `/root/morning-briefing/` |
| `openclaw-morning-briefing/deploy/agents/main/SOUL.md` | `~/.openclaw/workspace/SOUL.md` |
| `openclaw-morning-briefing/deploy/agents/morning/SOUL.md` | `~/.openclaw/workspace/morning/SOUL.md` + `~/.openclaw/agents/morning/SOUL.md` |
| `openclaw-wechat-writer/deploy/agents/wechat-writer/SOUL.md` | `~/.openclaw/workspace/wechat-writer/SOUL.md` + `~/.openclaw/agents/wechat-writer/SOUL.md` |
| `openclaw-wechat-writer/deploy/scripts/send-articles.py` | `~/.openclaw/scripts/send-articles.py` |

## 常用运维命令

```bash
sudo systemctl status openclaw        # 服务状态
sudo systemctl restart openclaw        # 重启
journalctl -u openclaw -f             # 实时日志
journalctl -u openclaw --since '1 hour ago'  # 最近日志
openclaw cron list                     # 定时任务
openclaw cron run <job-id>             # 手动触发
```

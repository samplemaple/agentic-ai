# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## 服务器信息

- **云服务器**：通过 Tailscale 私有网络访问
- **Tailscale 地址**：[your_tailscale_hostname].ts.net
- **SSH 用户名**：root
- **SSH 密码**：见 `/opt/openclaw.env` 或本地 `.env` 文件
- **SSH 工具**：Tabby

## Agent 体系

| Agent | 实例名 | 职责 |
|-------|--------|------|
| 路由助手 | main | 意图识别、任务分发 |
| 晨间执行官 | morning | 晨间简报、晚间日报、周五周报、临时任务 |

## MCP 工具

| 工具 | 用途 |
|------|------|
| fetch | 天气 API、RSS 新闻抓取 |
| filesystem | 读写 /root/morning-briefing/ 下的数据文件 |

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

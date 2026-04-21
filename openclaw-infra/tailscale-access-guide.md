# 通过 Tailscale 私有网络访问 OpenClaw 服务器

## 前提条件

- 一台已部署 OpenClaw 的云服务器（已安装 Tailscale）
- 你要访问的客户端设备（Windows/Mac/Linux/手机）

## 1. 安装 Tailscale 客户端

| 平台 | 安装方式 |
|------|---------|
| Windows | https://tailscale.com/download/windows 下载安装包 |
| macOS | `brew install tailscale` 或 App Store 搜索 Tailscale |
| Linux | `curl -fsSL https://tailscale.com/install.sh \| sh` |
| iOS/Android | 应用商店搜索 Tailscale |

## 2. 登录 Tailscale 网络

```bash
# Linux/macOS
sudo tailscale up

# Windows
# 安装后托盘图标点击 Log in
```

登录时使用与服务器相同的 Tailscale 账号（或同一 tailnet）。

## 3. 确认设备在同一 tailnet

```bash
tailscale status
```

输出中应能看到你的服务器节点，类似：

```
100.x.x.x   iv-yekai6mkn4s...  linux   -
100.x.x.x   your-laptop         windows -
```

## 4. SSH 连接服务器

```bash
ssh root@<你的服务器tailscale域名>.ts.net
```

Tailscale 域名格式：`<hostname>.<tailnet-name>.ts.net`

## 5. 访问 OpenClaw 控制台

OpenClaw Gateway 默认监听 `127.0.0.1:18789`（仅本地）。要通过 Tailscale 访问，有两种方式：

### 方式 A：SSH 端口转发（推荐，无需改配置）

```bash
ssh -L 18789:127.0.0.1:18789 root@<服务器>.ts.net
```

然后浏览器打开 `http://localhost:18789`

### 方式 B：Tailscale Serve（暴露给 tailnet）

```bash
# 在服务器上执行
sudo tailscale serve --bg 18789
```

然后在任意 tailnet 设备上访问 `https://<服务器>.ts.net/`

关闭：`sudo tailscale serve --bg off`

## 6. OpenClaw CLI 远程操作

在本地机器上通过 SSH 执行 OpenClaw 命令：

```bash
# 查看 cron 任务
ssh root@<服务器>.ts.net "openclaw cron list"

# 手动触发任务
ssh root@<服务器>.ts.net "openclaw cron run <job-id>"

# 查看服务状态
ssh root@<服务器>.ts.net "openclaw status"

# 查看日志
ssh root@<服务器>.ts.net "openclaw doctor"
```

## 7. 文件部署（从本地到服务器）

```bash
# 部署 Agent SOUL.md
scp path/to/SOUL.md root@<服务器>.ts.net:~/.openclaw/agents/<agent-id>/SOUL.md

# 部署数据文件
scp path/to/config.json root@<服务器>.ts.net:/root/morning-briefing/config.json
```

## 安全说明

- Tailscale 使用 WireGuard 加密，所有流量端到端加密
- 服务器不需要开放任何公网端口
- OpenClaw Gateway 保持 `bind: loopback`，只通过 SSH 转发或 Tailscale Serve 访问
- 建议开启 Tailscale ACL 限制哪些设备可以访问服务器

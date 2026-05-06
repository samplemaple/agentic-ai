#!/usr/bin/env python3
"""OpenClaw 部署脚本 — 通过 SSH 自动完成部署"""

import paramiko
import time
import sys

HOST = "101.47.152.111"
USER = "root"
PASSWORD = "Yby19941202.."
REPO_URL = "https://github.com/samplemaple/agentic-ai.git"
DEEPSEEK_KEY = "sk-0310f5a21439463a94794f511fbaebaa"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

def run(cmd, timeout=60, sudo=False):
    if sudo:
        cmd = f"echo '{PASSWORD}' | sudo -S bash -c '{cmd}'"
    print(f"  $ {cmd[:120]}...")
    stdin, stdout, stderr = client.exec_command(cmd, timeout=timeout)
    exit_code = stdout.channel.recv_exit_status()
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if exit_code != 0:
        print(f"  ⚠️  exit={exit_code}, err={err[:200]}")
    return out, err, exit_code

def run_interactive(commands, timeout=120):
    """Send multiple commands interactively via shell"""
    channel = client.invoke_shell()
    time.sleep(1)
    output = ""
    for cmd in commands:
        print(f"  > {cmd[:100]}")
        channel.send(cmd + "\n")
        time.sleep(2)
    while channel.recv_ready():
        output += channel.recv(4096).decode()
    channel.close()
    return output

print("=" * 50)
print("OpenClaw 一键部署 — Step 1~4 自动化")
print("=" * 50)

print("\n[1/6] 连接服务器...")
client.connect(HOST, username=USER, password=PASSWORD, look_for_keys=False)
print("  ✅ 已连接")

print("\n[2/6] Step 1: 系统更新 + 安装 git...")
run("apt update && apt upgrade -y && apt install -y curl git", timeout=120)
print("  ✅ 系统已更新")

print("\n[3/6] Step 2: 安装 Node.js 24 + OpenClaw...")
# Check Node.js version
out, _, _ = run("node -v 2>/dev/null || echo 'no node'")
if "no node" in out or "v" not in out:
    run("curl -fsSL https://deb.nodesource.com/setup_24.x | bash -", timeout=60)
    run("apt install -y nodejs", timeout=60)

out, _, _ = run("node -v")
print(f"  Node.js: {out}")

# Install OpenClaw
run("npm install -g openclaw@2026.4.22", timeout=120)
run("mkdir -p /root/.openclaw/completions")
run("openclaw completion > /root/.openclaw/completions/openclaw.bash 2>/dev/null || true")
print("  ✅ OpenClaw 已安装")

print("\n[4/6] Step 3: 配置 API Key + 启动 Gateway...")
# 写环境变量
env_content = f"""OPENAI_API_KEY={DEEPSEEK_KEY}
OPENAI_BASE_URL=https://api.deepseek.com/v1
"""
# 用 heredoc 方式创建文件
run(f"cat > /opt/openclaw.env << 'EOF'\n{env_content}\nEOF")
run("chmod 600 /opt/openclaw.env")
print("  ✅ API 配置完成 (DeepSeek)")

run("openclaw config set gateway.mode local 2>/dev/null || true")

# 创建 systemd 服务
bin_path, _, _ = run("which openclaw")
bin_path = bin_path.strip()

service_content = f"""[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
EnvironmentFile=/opt/openclaw.env
Environment=HOME=/root
ExecStart={bin_path} gateway --port 18789
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
"""

run(f"cat > /etc/systemd/system/openclaw.service << 'EOF'\n{service_content}\nEOF")
run("systemctl daemon-reload")
run("systemctl enable openclaw")

# 清理端口并启动
run("ss -tlnp | grep ':18789' && (fuser -k 18789/tcp 2>/dev/null; sleep 2) || true")
run("systemctl start openclaw")
time.sleep(3)

status, _, _ = run("systemctl is-active openclaw")
if "active" in status:
    print("  ✅ Gateway 已启动并设为开机自启")
else:
    print("  ⚠️  请稍后检查: systemctl status openclaw")

print("\n[5/6] Step 4: Tailscale 已安装，跳过")
print(f"  Tailscale IP: 100.116.4.63")
print(f"  设备名: iv-yekai6mkn4sobos7uo0f")

print("\n[6/6] 配置 DNS...")
run("mkdir -p /etc/systemd/resolved.conf.d")
run("""cat > /etc/systemd/resolved.conf.d/public-dns.conf << 'EOF'
[Resolve]
DNS=8.8.8.8 8.8.4.4
EOF""")
run("systemctl restart systemd-resolved 2>/dev/null || true")
print("  ✅ DNS 配置完成")

print("\n" + "=" * 50)
print("  ✅ Step 1-4 自动化完成！")
print("=" * 50)
print("""
接下来请手动完成 Step 5（必须）：

5.1  Tailscale 认证（如未完成）:
      sudo tailscale up

5.2  开启 Tailscale Serve:
      tailscale serve --bg 18789

5.3  预获取 HTTPS 证书:
      tailscale status --self --json | grep -m1 DNSName | tr -d ' ",' | cut -d: -f2 | sed 's/\\.$//'
      tailscale cert <上面输出的域名>

5.4  配置 allowedOrigins:
      openclaw config set gateway.controlUi.allowedOrigins '["http://localhost:18789","http://127.0.0.1:18789","https://<你的域名>"]'
      systemctl restart openclaw

5.5  获取 Dashboard 地址:
      openclaw dashboard --no-open

5.6  浏览器访问配对:
      openclaw devices list
      openclaw devices approve <Request 列中的 ID>
""")

client.close()

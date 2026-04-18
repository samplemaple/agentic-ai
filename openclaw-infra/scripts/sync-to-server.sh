#!/bin/bash
# ============================================================
# 将本地项目同步到云服务器（排除 .kiro 目录）
#
# 使用方法（在 Windows Git Bash 或 WSL 中执行）：
#   chmod +x sync-to-server.sh
#   ./sync-to-server.sh
#
# 如果使用 PowerShell，请直接运行：
#   bash ./openclaw-infra/scripts/sync-to-server.sh
# ============================================================

# ===== 配置区域（按需修改）=====
SERVER_USER="root"
SERVER_IP="101.47.152.111"
LOCAL_DIR="/mnt/d/AIStudy/agentic-ai/"
REMOTE_DIR="~/agentic-ai/"
# ==============================

echo "=========================================="
echo "  同步本地项目到云服务器"
echo "  ${LOCAL_DIR} → ${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}"
echo "=========================================="
echo ""

# 使用 rsync 同步，排除 .kiro 和 .git 目录
if command -v rsync &> /dev/null; then
    echo "使用 rsync 同步（增量传输）..."
    rsync -avz --progress \
        --exclude='.kiro' \
        --exclude='.git' \
        "$LOCAL_DIR" "${SERVER_USER}@${SERVER_IP}:${REMOTE_DIR}"
else
    # 如果没有 rsync，用 scp（不支持排除，先打包再传）
    echo "未检测到 rsync，使用 tar + scp 方式..."
    TEMP_TAR="/tmp/agentic-ai-sync.tar.gz"
    tar -czf "$TEMP_TAR" -C "$(dirname "$LOCAL_DIR")" \
        --exclude='.kiro' \
        --exclude='.git' \
        "$(basename "$LOCAL_DIR")"
    scp "$TEMP_TAR" "${SERVER_USER}@${SERVER_IP}:/tmp/"
    ssh "${SERVER_USER}@${SERVER_IP}" "mkdir -p ${REMOTE_DIR} && tar -xzf /tmp/agentic-ai-sync.tar.gz -C $(dirname ${REMOTE_DIR}) && rm /tmp/agentic-ai-sync.tar.gz"
    rm -f "$TEMP_TAR"
fi

echo ""
echo "✅ 同步完成"

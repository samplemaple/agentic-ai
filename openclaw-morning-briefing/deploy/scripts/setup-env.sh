#!/bin/bash
# 配置凭证安全与环境变量
# 创建 /opt/openclaw.env 文件，存放 API Key 等凭证
# 设置文件权限为 600，确保只有 root 可读
#
# 使用方法：在云服务器上执行
#   chmod +x setup-env.sh
#   sudo ./setup-env.sh

ENV_FILE="/opt/openclaw.env"

echo ">>> 创建环境变量文件 ${ENV_FILE}..."

# 如果文件已存在，提示用户
if [ -f "$ENV_FILE" ]; then
    echo ">>> 文件已存在，将追加晨间简报相关的环境变量..."
    echo "" >> "$ENV_FILE"
    echo "# ==================== 晨间执行官 ====================" >> "$ENV_FILE"
else
    cat > "$ENV_FILE" << 'EOF'
# ============================================================
# OpenClaw 环境变量配置文件
# 存放 API Key 等凭证信息，不要提交到 Git
# ============================================================

# ==================== 晨间执行官 ====================
EOF
fi

# 追加和风天气 API Key（占位符）
cat >> "$ENV_FILE" << 'EOF'
# 和风天气 API Key（免费版每天 1000 次调用）
# 注册地址：https://dev.qweather.com
QWEATHER_API_KEY=你的和风天气API_Key
EOF

echo ">>> 设置文件权限为 600..."
chmod 600 "$ENV_FILE"

echo ">>> 验证文件权限..."
ls -la "$ENV_FILE"

echo ">>> 完成。请编辑 ${ENV_FILE} 填入你的真实 API Key。"

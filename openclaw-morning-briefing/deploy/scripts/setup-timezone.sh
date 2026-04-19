#!/bin/bash
# 设置云服务器时区为 Asia/Shanghai
# 确保 Heartbeat 的 cron 表达式按上海时间触发
#
# 使用方法：在云服务器上执行
#   chmod +x setup-timezone.sh
#   sudo ./setup-timezone.sh

echo ">>> 设置服务器时区为 Asia/Shanghai..."
sudo timedatectl set-timezone Asia/Shanghai

echo ">>> 验证时区设置..."
timedatectl

echo ">>> 时区设置完成。当前时间："
date

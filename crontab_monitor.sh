#!/bin/bash
# 启动 linux.do 监控服务
# 用法: ./crontab_monitor.sh
# 或者直接: TELEGRAM_BOT_TOKEN=xxx TELEGRAM_CHAT_ID=yyy python3 monitor_linux_do.py

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 检查依赖
if ! command -v python3 &> /dev/null; then
    echo "错误: 需要 python3"
    exit 1
fi

# 安装依赖
pip3 install requests beautifulsoup4 --quiet 2>/dev/null || pip3 install requests beautifulsoup4

# 设置环境变量（如果未设置）
export TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
export TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"

# 运行监控
cd "$SCRIPT_DIR"
python3 monitor_linux_do.py

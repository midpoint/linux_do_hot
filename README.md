# linux.do Hot Monitor

监控 [linux.do/hot](https://linux.do/hot) 热门话题，推送到 Telegram。

## 功能

- 每 3 小时自动检查 linux.do 热门话题
- 检测新增帖子，单独推送每条（标题 + 第一条完整内容）
- 使用环境变量配置，简单安全

## 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（从 @BotFather 获取） | 是 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID（用户 ID 或频道 ID） | 是 |
| `PROXY_URL` | 代理服务器地址，如 `http://127.0.0.1:20171` | 否（可选） |
| `CHECK_INTERVAL` | 检查间隔（秒），默认 10800（3小时） | 否 |

## 使用方法

### 1. 克隆项目

```bash
git clone https://github.com/midpoint/linux_do_hot.git
cd linux_do_hot
```

### 2. 安装依赖

```bash
pip3 install requests beautifulsoup4
```

### 3. 配置并运行

```bash
export TELEGRAM_BOT_TOKEN="你的BotToken"
export TELEGRAM_CHAT_ID="你的ChatID"
export PROXY_URL="http://127.0.0.1:20171"  # 如需要代理

python3 monitor_linux_do.py
```

### 4. 设置定时任务（每3小时）

```bash
crontab -e

# 添加以下行：
0 */3 * * * cd /path/to/linux_do_hot && TELEGRAM_BOT_TOKEN="xxx" TELEGRAM_CHAT_ID="yyy" PROXY_URL="http://xxx" python3 monitor_linux_do.py >> /tmp/linux_do_monitor.log 2>&1
```

## 状态文件

脚本会在同目录生成 `.hot_state.json` 保存已推送的帖子 ID，重启后会自动跳过已推送的内容。

## License

MIT

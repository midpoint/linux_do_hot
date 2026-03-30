# linux.do Hot Monitor

监控 [linux.do/hot](https://linux.do/hot) 热门话题，推送到 Telegram。

## 功能

- 每天北京时间 6:00 和 14:00 自动检查 linux.do 热门话题（通过 GitHub Actions）
- 检测新增帖子，推送标题和链接
- 使用 ScrapingAnt API 解决 GitHub Actions 无法直接访问的问题
- 所有配置通过 GitHub Secrets 管理，安全便捷

## 环境变量（GitHub Secrets）

| 变量 | 说明 | 必需 |
|------|------|------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token（从 @BotFather 获取） | 是 |
| `TELEGRAM_CHAT_ID` | Telegram Chat ID（用户 ID 或频道 ID） | 是 |
| `SCRAPINGANT_API_KEY` | ScrapingAnt API Key（用于网页抓取） | 是 |

## 部署步骤

### 1. 注册 ScrapingAnt

1. 访问 [ScrapingAnt](https://scrapingant.com/) 注册账号
2. 在 Dashboard 获取 API Key

### 2. 配置 GitHub Secrets

1. 打开仓库 **Settings → Secrets and variables → Actions**
2. 添加以下 Secrets：
   - `TELEGRAM_BOT_TOKEN`: 你的 Telegram Bot Token
   - `TELEGRAM_CHAT_ID`: 你的 Telegram Chat ID
   - `SCRAPINGANT_API_KEY`: ScrapingAnt API Key

### 3. 手动触发测试

在 GitHub 仓库页面：
- 点击 **Actions** 标签
- 选择 **Monitor linux.do/hot** workflow
- 点击 **Run workflow** 手动触发测试

## 定时任务

- 每天北京时间 6:00（UTC 22:00）
- 每天北京时间 14:00（UTC 06:00）

## 本地运行

```bash
# 克隆项目
git clone https://github.com/midpoint/linux_do_hot.git
cd linux_do_hot

# 安装依赖
pip3 install requests beautifulsoup4

# 配置环境变量
export TELEGRAM_BOT_TOKEN="你的BotToken"
export TELEGRAM_CHAT_ID="你的ChatID"
export SCRAPINGANT_API_KEY="你的ScrapingAntKey"

# 运行
python3 monitor_linux_do.py
```

## 状态文件

脚本会在同目录生成 `.hot_state.json` 保存已推送的帖子 ID，重启后会自动跳过已推送的内容。

## License

MIT

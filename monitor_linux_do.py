#!/usr/bin/env python3
"""监控 linux.do/hot 页面，推送最新内容到 Telegram"""

import os
import sys
import json
import time
import hashlib
import logging
from datetime import datetime

import requests
from bs4 import BeautifulSoup

# ============ 配置区 ============
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
TARGET_URL = "https://linux.do/hot"
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".hot_state.json")
MAX_CONTENT_LENGTH = 3500  # Telegram 消息最大 4096，保留空间给标题等
SCRAPINGANT_API_KEY = os.getenv("SCRAPINGANT_API_KEY", "")  # ScrapingAnt API Key
# =================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


def get_state() -> dict:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_state(state: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def fetch_url(url: str) -> tuple[str, str]:
    """使用 ScrapingAnt 获取页面内容"""
    if not SCRAPINGANT_API_KEY:
        # 如果没有 API Key，直接尝试本地请求
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
            return resp.text, ""
        except Exception as e:
            return "", str(e)

    api_url = f"https://api.scrapingant.com/v2/frames?url={url}&x-api-key={SCRAPINGANT_API_KEY}"
    try:
        resp = requests.get(api_url, timeout=60)
        if resp.status_code != 200:
            return "", f"API返回状态码: {resp.status_code}"
        return resp.text, ""
    except Exception as e:
        return "", str(e)


def fetch_hot_items() -> tuple[list, str]:
    """获取 linux.do/hot 页面的热门内容"""
    html_content, error = fetch_url(TARGET_URL)
    if error:
        log.error(f"获取页面失败: {error}")
        return [], error

    soup = BeautifulSoup(html_content, "html.parser")
    items = []

    for a_tag in soup.select("a.raw-link"):
        try:
            title = a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if len(title) > 3 and "/t/topic/" in link:
                if not link.startswith("http"):
                    link = "https://linux.do" + link
                item_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
                items.append({"id": item_id, "title": title, "link": link})
        except Exception:
            continue

    if not items:
        for a_tag in soup.find_all("a", href=True):
            try:
                link = a_tag.get("href", "")
                if "/t/topic/" in link:
                    title = a_tag.get_text(strip=True)
                    if len(title) > 3:
                        if not link.startswith("http"):
                            link = "https://linux.do" + link
                        item_id = hashlib.md5(f"{title}{link}".encode()).hexdigest()[:12]
                        items.append({"id": item_id, "title": title, "link": link})
            except Exception:
                continue

    log.info(f"获取到 {len(items)} 条热门内容")
    return items, ""


def fetch_first_post_content(topic_url: str) -> str:
    """获取帖子的第一条完整内容"""
    html_content, error = fetch_url(topic_url)
    if error:
        log.error(f"获取帖子失败: {error}")
        return ""

    soup = BeautifulSoup(html_content, "html.parser")
    posts = soup.select("div.post")

    if not posts:
        return ""

    first_post = posts[0]
    content_parts = []

    for child in first_post.find_all(recursive=False):
        text = child.get_text(strip=True)
        # 过滤图片和空白
        if text and not text.startswith("image") and not text.startswith("similarweb"):
            content_parts.append(text)

    content = "\n".join(content_parts)
    return content


def send_telegram(message: str) -> bool:
    """发送 Telegram 消息"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        resp = requests.post(url, json=payload, timeout=15)
        result = resp.json()
        if not result.get("ok"):
            log.error(f"Telegram API 错误: {result}")
            return False
        return True
    except Exception as e:
        log.error(f"发送 Telegram 消息失败: {e}")
        return False


def send_post(item: dict) -> bool:
    """发送单个帖子（标题 + 第一条内容）"""
    title = item["title"]
    link = item["link"]

    # 获取第一条内容
    content = fetch_first_post_content(link)
    if not content:
        log.warning(f"无法获取 {title} 的内容")
        content = "(内容获取失败)"

    # 截断过长的内容
    if len(content) > MAX_CONTENT_LENGTH:
        content = content[:MAX_CONTENT_LENGTH] + "\n\n... (内容过长已截断)"

    # 组合消息
    message = f"📌 <b>{title}</b>\n\n{content}\n\n🔗 <a href=\"{link}\">查看原文</a>"

    return send_telegram(message)


def main():
    log.info("=" * 50)
    log.info("linux.do/hot 监控服务启动")
    log.info(f"目标: {TARGET_URL}")
    if SCRAPINGANT_API_KEY:
        log.info("使用 ScrapingAnt API")
    log.info("=" * 50)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prev_state = get_state()
    prev_ids = set(prev_state.get("ids", []))

    log.info(f"上次记录: {len(prev_ids)} 条")

    try:
        items, error = fetch_hot_items()

        if error:
            # 获取页面失败，发送错误信息
            msg = f"❌ <b>linux.do 监控异常</b>\n\n⏰ {now}\n📭 获取页面失败\n🔗 {error}"
            send_telegram(msg)
            return

        if not items:
            msg = f"⚠️ <b>linux.do 监控</b>\n\n⏰ {now}\n📭 未能获取到内容"
            send_telegram(msg)
            return

        current_ids = set(item["id"] for item in items)
        new_ids = current_ids - prev_ids

        if new_ids and prev_ids:
            log.info(f"检测到 {len(new_ids)} 条新内容!")
            new_items = [item for item in items if item["id"] in new_ids]

            for item in new_items:
                log.info(f"推送: {item['title'][:50]}")
                if send_post(item):
                    log.info("  推送成功")
                else:
                    log.error("  推送失败")
                time.sleep(1)

        elif not prev_ids:
            log.info(f"初始化完成，记录 {len(items)} 条")
            msg = f"✅ <b>linux.do 监控初始化</b>\n\n⏰ {now}\n📭 记录 {len(items)} 条热门帖子"
            send_telegram(msg)
        else:
            log.info("无新内容")
            msg = f"✅ <b>linux.do 检查完成</b>\n\n⏰ {now}\n📭 暂无新热门帖子"
            send_telegram(msg)

        save_state({"ids": list(current_ids), "items": items})

    except Exception as e:
        log.error(f"异常: {e}")
        msg = f"❌ <b>linux.do 监控异常</b>\n\n⏰ {now}\n📭 {str(e)}"
        try:
            send_telegram(msg)
        except:
            pass


if __name__ == "__main__":
    if "YOUR_BOT_TOKEN" in TELEGRAM_BOT_TOKEN or "YOUR_CHAT_ID" in TELEGRAM_CHAT_ID:
        print("请设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量!")
        sys.exit(1)

    main()

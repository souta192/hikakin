import os
import asyncio
from fastapi import FastAPI
from .channels import CHANNELS
from .notifier import Notifier

# 環境変数からWebhook URLとチェック間隔
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
INTERVAL_SEC = int(os.getenv("CHECK_INTERVAL_SECONDS", "300"))

notifier = Notifier(
    webhook_url=WEBHOOK_URL,
    channels=CHANNELS,
    interval_sec=INTERVAL_SEC,
)

app = FastAPI(
    title="YouTube -> Discord Notifier",
    description="YouTubeチャンネルの新着動画をDiscord Webhookに自動通知するWebサービス (Render対応版)",
    version="1.0.0",
)


@app.on_event("startup")
async def startup_event():
    """
    サービス起動時にバックグラウンドポーラーを走らせる。
    Render みたいな常時稼働Webサービス環境を想定。
    """
    if not notifier.webhook_url:
        # Webhook未設定は致命的なので止める
        raise RuntimeError("環境変数 DISCORD_WEBHOOK_URL が設定されていません。")

    async def poller():
        while True:
            results = notifier.check_once()
            print("[poller]", results)
            await asyncio.sleep(notifier.interval_sec)

    asyncio.create_task(poller())


@app.get("/status")
def status():
    """
    現在の状態を返す。
    """
    return {
        "last_check_unix": notifier.last_check,
        "last_check_iso": notifier.last_check_iso(),
        "interval_seconds": notifier.interval_sec,
        "channels": CHANNELS,
        "known_latest_video_ids": notifier.state,
    }


@app.post("/check-now")
def check_now():
    """
    手動トリガーで即チェックしたいときに叩く。
    """
    results = notifier.check_once()
    return {
        "checked_at": notifier.last_check_iso(),
        "results": results,
    }

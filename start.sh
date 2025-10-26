#!/bin/sh
# Renderが $PORT を割り当てるのでそこを使う
# 環境変数 DISCORD_WEBHOOK_URL は Render 側で設定しておくこと
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

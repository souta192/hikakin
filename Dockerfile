# ベースイメージ (安定のPython 3.12系を想定)
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係をコピー＆インストール
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# アプリ本体をコピー
COPY app /app/app
COPY start.sh /app/start.sh

# state.jsonを保存する永続ディスクをここにマウントする想定
# RenderのDisk機能で /data を永続化させる
RUN mkdir -p /data && chmod 777 /data
ENV STATE_DIR=/data
ENV CHECK_INTERVAL_SECONDS=300

# Render は $PORT を渡してくるのでそれを使ってuvicorn起動
# DISCORD_WEBHOOK_URL もRenderの環境変数で渡す
CMD ["./start.sh"]

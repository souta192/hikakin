# ベースイメージ
FROM python:3.12-slim

# コンテナ内の作業ディレクトリ
WORKDIR /app

# 依存ファイルコピー＆インストール
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# アプリ本体コピー
COPY app /app/app
COPY start.sh /app/start.sh

# start.sh を実行可能にする
# /data は Render の永続ディスクをマウントする場所 (STATE_DIRで使う)
RUN chmod +x /app/start.sh && \
    mkdir -p /data && chmod 777 /data

# アプリが使う環境変数のデフォルト
ENV STATE_DIR=/data
ENV CHECK_INTERVAL_SECONDS=300

# Renderがくれる $PORT で uvicorn を起動する
CMD ["/app/start.sh"]

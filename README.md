# YouTube → Discord Notifier (Render用)

ヒカキン系チャンネルの新着動画を監視して、出た瞬間にDiscord Webhookへ通知する常時稼働サービス。  
これを Render.com みたいなホスティングにデプロイして、サーバーなしで動かす想定。

## なにが動くの？
- FastAPI で `/status` と `/check-now` のエンドポイントを公開
- 起動中はバックグラウンドで 5分おき(初期設定)に YouTube RSS をチェック
- 新しい動画を見つけたら Discord Webhook にサムネ付きで投稿
- 同じ動画を二重送信しないように、`state.json` を永続ボリューム(`/data`)に保存

ヒカキン本人のチャンネル (例: HikakinTV / HikakinGames / HikakinBlog) のチャンネルIDを使って  
`https://www.youtube.com/feeds/videos.xml?channel_id=<チャンネルID>`  
を監視します。citeturn0search5turn0search6turn0search9  
- HikakinTV のチャンネルIDは `UCZf__ehlCEBPop-_sldpBUQ`。citeturn0search0turn0search1  
- HikakinGames は `UCX1xppLvuj03ubLio8jslyA`。citeturn0search1turn0search2  
- HikakinBlog は `UCQMoeRP9SDaFipXDBIp3pFA`。citeturn0search1turn0search2  

## フォルダ構成
```text
ytdiscord-render/
  README.md
  requirements.txt
  Dockerfile
  render.yaml
  start.sh
  app/
    __init__.py
    channels.py      ← 監視したいYouTubeチャンネル一覧 (ヒカキンTVなど)
    notifier.py      ← RSSを確認してDiscordに投げるロジック
    main.py          ← FastAPI本体。バックグラウンドでポーリングも開始
```

## 動作イメージ
- RenderがこのリポジトリをDockerでビルド・起動する
- Render側から `DISCORD_WEBHOOK_URL` (環境変数) を渡す
- `CHECK_INTERVAL_SECONDS` でポーリング間隔(秒)を指定できる (例: 300 = 5分)
- `STATE_DIR` は `/data` にマウントされる永続ディスク。`state.json` がここに置かれる

### `/status` (GET)
現在の状態をJSONで返す。  
- last_checkの時刻  
- 監視対象チャンネル一覧  
- それぞれの最新通知済み動画ID など

### `/check-now` (POST)
今すぐチェックして、必要ならDiscordに送る。手動テスト用。

---

## Renderへのデプロイ手順 (Dockerとして)

1. このフォルダをGitHubリポジトリにプッシュする  
   (例: `youtube-discord-notifier` みたいな名前)

2. Renderのダッシュボードで「New +」→「Web Service」→ GitHubリポジトリを選択  
   - Environment: Docker を選ぶ  
   - Health Check Path: `/status` を指定できるなら指定

3. 環境変数を設定  
   - `DISCORD_WEBHOOK_URL` → DiscordのWebhook URL (必須)
   - `CHECK_INTERVAL_SECONDS` → "300" など (省略可、デフォ300)
   - `STATE_DIR` → `/data` にする (省略可、Dockerfileで`/data`にしてある)

4. 永続ディスクの設定  
   - Renderの「Disks」機能で `/data` に 1GB とかをマウント  
   - これで state.json がデプロイ間で消えない

5. デプロイすると、コンテナが `uvicorn` でFastAPIを `0.0.0.0:$PORT` に公開する  
   Renderは外部公開URLをくれるので、そこの `/status` を叩けば動作確認できる

> 注意: 無料/スリープするプランだとサーバーが止まってる間はチェックも止まる。  
> 24h貼り付きで通知したいなら、止まらないプラン/インスタンスにする。  
> (プラン名や料金は変わることがあるので実際のRender側を確認してください)

---

## ローカルで試したい場合 (Dockerなし)
1. 環境変数をセットして起動:
   ```bash
   export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/xxx/yyy"
   export CHECK_INTERVAL_SECONDS=300
   export STATE_DIR="./data"
   mkdir -p ./data
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

2. ブラウザで `http://localhost:8000/status`  
   手動チェックは `curl -X POST http://localhost:8000/check-now`

---

## チャンネルの追加・削除
`app/channels.py` を編集してOK:

```python
CHANNELS = [
    {"name": "HikakinTV",    "channel_id": "UCZf__ehlCEBPop-_sldpBUQ"},
    {"name": "HikakinGames", "channel_id": "UCX1xppLvuj03ubLio8jslyA"},
    {"name": "HikakinBlog",  "channel_id": "UCQMoeRP9SDaFipXDBIp3pFA"},
    # {"name": "別チャンネル", "channel_id": "UC.............."},
]
```

Renderにデプロイし直すと、そのチャンネルも監視対象になる。

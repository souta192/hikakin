"""
監視対象のYouTubeチャンネル一覧。

"name": Discordに表示するラベル
"feed_url": そのチャンネルのRSSフィードURL
  - channel_id がわかるチャンネルは ?channel_id=...
  - ユーザー名(例: hikakincliptv)で公開されてるチャンネルは ?user=... にできる

この feed_url を定期的にGETして最新動画をチェックする。
"""

CHANNELS = [
    {
        "name": "HikakinTV",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCZf__ehlCEBPop-_sldpBUQ",
    },
    {
        "name": "HikakinGames",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCX1xppLvuj03ubLio8jslyA",
    },
    {
        "name": "HikakinBlog",
        "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UCQMoeRP9SDaFipXDBIp3pFA",
    },
    {
        "name": "HikakinClipTV",
        # 公式切り抜きチャンネル（Twitch配信のクリップを上げてる新チャンネル）
        # ユーザー名が "hikakincliptv" として公開されてるので user= でRSSが取れる
        "feed_url": "https://www.youtube.com/feeds/videos.xml?user=hikakincliptv",
    },
    # 追加したいチャンネルがあればこの下に同じ形式で足すだけ
    # {
    #     "name": "SomeOtherChannel",
    #     "feed_url": "https://www.youtube.com/feeds/videos.xml?channel_id=UC..............",
    # },
]

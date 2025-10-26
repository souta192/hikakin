import os
import time
import json
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

# STATE_DIR は Render の永続ディスク (/data) を想定
STATE_DIR = os.getenv("STATE_DIR", "/data")
os.makedirs(STATE_DIR, exist_ok=True)

STATE_FILE = os.path.join(STATE_DIR, "state.json")


class Notifier:
    """
    - CHANNELS にある feed_url を定期的にチェック
    - 新しい動画があれば Discord Webhook に通知
    - 通知済み動画のIDは state.json に保存して二重送信を防止
    """

    def __init__(self, webhook_url: str, channels: List[Dict[str, str]], interval_sec: int = 300):
        self.webhook_url = webhook_url
        self.channels = channels
        self.interval_sec = interval_sec
        self.state = self._load_state()  # {feed_url: last_video_id, ...}
        self.last_check = 0.0

    def _load_state(self) -> Dict[str, str]:
        if not os.path.exists(STATE_FILE):
            return {}
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _save_state(self) -> None:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

    def _fetch_latest_from_feed(self, feed_url: str) -> Dict[str, str] | None:
        """
        指定されたYouTube RSS(Atom)フィードURL(feed_url)を叩いて
        一番新しい動画エントリだけを返す。

        戻り値の例:
        {
            "video_id": "...",
            "title": "...",
            "url": "https://www.youtube.com/watch?v=...",
            "published": "2025-01-23T12:34:56+00:00"
        }

        見つからなければ None
        """
        resp = requests.get(feed_url, timeout=10)
        resp.raise_for_status()

        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
            "media": "http://search.yahoo.com/mrss/",
        }

        root = ET.fromstring(resp.text)
        entry = root.find("atom:entry", ns)
        if entry is None:
            return None

        video_id_elem = entry.find("yt:videoId", ns)
        title_elem = entry.find("atom:title", ns)
        published_elem = entry.find("atom:published", ns)

        link_url = None
        for link_candidate in entry.findall("atom:link", ns):
            if link_candidate.get("rel") == "alternate":
                link_url = link_candidate.get("href")
                break

        if not (video_id_elem is not None and title_elem is not None and link_url):
            return None

        return {
            "video_id": video_id_elem.text,
            "title": title_elem.text,
            "url": link_url,
            "published": published_elem.text if published_elem is not None else "",
        }

    def _send_discord_notification(self, channel_name: str, video_info: Dict[str, str]) -> None:
        """
        Discord Webhookに送る。
        サムネイルは YouTube のサムネURLをembedに入れる。
        """
        thumb_url = f"https://i.ytimg.com/vi/{video_info['video_id']}/hqdefault.jpg"

        content_text = (
            f"📢 {channel_name} の新着動画！\n"
            f"{video_info['title']}\n"
            f"{video_info['url']}"
        )

        payload = {
            "content": content_text,
            "embeds": [
                {
                    "title": video_info["title"],
                    "url": video_info["url"],
                    "description": f"公開時刻: {video_info['published']}",
                    "thumbnail": {
                        "url": thumb_url
                    },
                }
            ],
        }

        r = requests.post(self.webhook_url, json=payload, timeout=10)
        if r.status_code >= 400:
            print("Discord送信エラー:", r.status_code, r.text)
        else:
            print(f"[OK] Discord送信: {channel_name} -> {video_info['title']}")

    def check_once(self) -> List[Dict[str, Any]]:
        """
        全チャンネルを1回ずつチェックして、必要ならDiscordに通知する。
        戻り値はログ用のリスト。
        """
        results = []
        now = time.time()

        for ch in self.channels:
            ch_name = ch["name"]
            feed_url = ch["feed_url"]

            try:
                latest = self._fetch_latest_from_feed(feed_url)
            except Exception as e:
                results.append({
                    "channel": ch_name,
                    "status": "error",
                    "error": str(e),
                })
                continue

            if latest is None:
                results.append({
                    "channel": ch_name,
                    "status": "no_entry",
                })
                continue

            last_sent_id = self.state.get(feed_url)

            if latest["video_id"] != last_sent_id:
                # 新作を検知→Discordへ通知
                self._send_discord_notification(ch_name, latest)

                # 状態更新
                self.state[feed_url] = latest["video_id"]
                self._save_state()

                results.append({
                    "channel": ch_name,
                    "status": "sent",
                    "video_title": latest["title"],
                    "video_url": latest["url"],
                })
            else:
                results.append({
                    "channel": ch_name,
                    "status": "no_new",
                    "video_title": latest["title"],
                })

        self.last_check = now
        return results

    def last_check_iso(self) -> str | None:
        if self.last_check == 0:
            return None
        return time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime(self.last_check))

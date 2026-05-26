import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import os

# YouTube RSS feeds for both AL.com channels
FEEDS = [
    "https://www.youtube.com/feeds/videos.xml?channel_id=UCXovZWLiLAQwhc07L_TuHYQ",  # Alabama Crimson Tide on AL.com
    "https://www.youtube.com/feeds/videos.xml?channel_id=UC2JSgw37hwXBA-4PVeVlwAg",  # Auburn Tigers on AL.com
]

# YouTube Atom feed namespace
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "yt": "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}

def parse_date(date_str):
    """Parse ISO 8601 date string to datetime object."""
    if date_str:
        date_str = date_str.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            pass
    return datetime.min.replace(tzinfo=timezone.utc)

def fetch_feed(url):
    """Fetch and parse a YouTube RSS feed, return list of entry dicts."""
    entries = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
        root = ET.fromstring(raw)

        channel_title_el = root.find("atom:title", NS)
        channel_title = channel_title_el.text if channel_title_el is not None else "AL.com"

        for entry in root.findall("atom:entry", NS):
            video_id_el = entry.find("yt:videoId", NS)
            title_el = entry.find("atom:title", NS)
            published_el = entry.find("atom:published", NS)
            updated_el = entry.find("atom:updated", NS)
            link_el = entry.find("atom:link", NS)
            author_el = entry.find("atom:author/atom:name", NS)

            # Media elements
            media_group = entry.find("media:group", NS)
            description_el = None
            thumbnail_el = None
            if media_group is not None:
                description_el = media_group.find("media:description", NS)
                thumbnail_el = media_group.find("media:thumbnail", NS)

            video_id = video_id_el.text if video_id_el is not None else ""
            title = title_el.text if title_el is not None else "Untitled"
            published_str = published_el.text if published_el is not None else ""
            updated_str = updated_el.text if updated_el is not None else published_str
            link = link_el.get("href", "") if link_el is not None else f"https://www.youtube.com/watch?v={video_id}"
            author = author_el.text if author_el is not None else channel_title
            description = description_el.text if description_el is not None else ""
            thumbnail_url = thumbnail_el.get("url", "") if thumbnail_el is not None else ""
            thumbnail_width = thumbnail_el.get("width", "480") if thumbnail_el is not None else "480"
            thumbnail_height = thumbnail_el.get("height", "360") if thumbnail_el is not None else "360"

            entries.append({
                "video_id": video_id,
                "title": title,
                "published": published_str,
                "updated": updated_str,
                "published_dt": parse_date(published_str),
                "link": link,
                "author": author,
                "description": description,
                "thumbnail_url": thumbnail_url,
                "thumbnail_width": thumbnail_width,
                "thumbnail_height": thumbnail_height,
            })

    except Exception as e:
        print(f"Error fetching {url}: {e}")

    return entries

def build_mrss(entries):
    """Build a merged MRSS XML string from a list of entry dicts."""
    now = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:media="http://search.yahoo.com/mrss/" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        "    <title>AL.com Sports - Alabama &amp; Auburn Videos</title>",
        "    <link>https://www.al.com</link>",
        "    <description>Combined video feed from Alabama Crimson Tide and Auburn Tigers on AL.com</description>",
        f"    <lastBuildDate>{now}</lastBuildDate>",
        '    <atom:link rel="self" type="application/rss+xml"/>',
    ]

    for e in entries:
        pub_date = e["published_dt"].strftime("%a, %d %b %Y %H:%M:%S +0000") if e["published_dt"] != datetime.min.replace(tzinfo=timezone.utc) else now

        def esc(text):
            return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        lines += [
            "    <item>",
            f"      <title>{esc(e['title'])}</title>",
            f"      <link>{esc(e['link'])}</link>",
            f"      <guid isPermaLink=\"false\">{esc(e['video_id'])}</guid>",
            f"      <pubDate>{pub_date}</pubDate>",
            f"      <author>{esc(e['author'])}</author>",
            f"      <description>{esc(e['description'])}</description>",
        ]

        if e["thumbnail_url"]:
            lines.append(
                f'      <media:thumbnail url="{esc(e["thumbnail_url"])}" width="{e["thumbnail_width"]}" height="{e["thumbnail_height"]}"/>'
            )
        if e["video_id"]:
            lines.append(
                f'      <media:content url="https://www.youtube.com/watch?v={e["video_id"]}" medium="video"/>'
            )

        lines.append("    </item>")

    lines += ["  </channel>", "</rss>"]
    return "\n".join(lines)

def main():
    print("Fetching feeds...")
    all_entries = []
    for url in FEEDS:
        entries = fetch_feed(url)
        print(f"  Got {len(entries)} entries from {url}")
        all_entries.extend(entries)

    # Sort newest to oldest
    all_entries.sort(key=lambda e: e["published_dt"], reverse=True)
    print(f"Total entries after merge: {len(all_entries)}")

    # Write output
    os.makedirs("docs", exist_ok=True)
    output_path = "docs/feed.xml"
    mrss = build_mrss(all_entries)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(mrss)

    print(f"Feed written to {output_path}")

if __name__ == "__main__":
    main()

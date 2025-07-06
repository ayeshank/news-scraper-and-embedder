import feedparser, pandas as pd, os, hashlib
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

CSV_FOLDER_PATH = "/home/ubuntu/shared_data/scraped_articles"
os.makedirs(CSV_FOLDER_PATH, exist_ok=True)
OUTPUT_FILE = os.path.join(CSV_FOLDER_PATH, "youtube_combined_dataset.csv")

def extract_video_id(video_url):
    if "watch?v=" in video_url:
        return parse_qs(urlparse(video_url).query).get("v", [None])[0]
    elif "youtu.be" in video_url:
        return video_url.split("/")[-1]
    return None

def fetch_rss_videos(channel_id, max_count=10):
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    feed = feedparser.parse(feed_url)
    videos = []
    for entry in feed.entries[:max_count]:
        video_id = extract_video_id(entry.link)
        if video_id:
            videos.append((video_id, entry.title, entry.link, entry.published))
    return videos

def get_transcript(video_id):
    try:
        return YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e1:
        print(f"⚠️ Failed: {e1}")
        return None

channels = {
    "aljazeera": "UCNye-wNBqNL5ZzHSJj3l8Bg"
}
combined_data = []
for source_name, channel_id in channels.items():
    for video_id, title, link, published in fetch_rss_videos(channel_id):
        transcript = get_transcript(video_id)
        if transcript:
            full_text = " ".join([entry['text'].strip() for entry in transcript])
            hex_val = hashlib.md5(f"{title}-{published}-{link}".encode()).hexdigest()
            combined_data.append({
                "title": title,
                "date": published.split("T")[0],
                "hex": hex_val,
                "article_url": link,
                "source": source_name,
                "article_content": full_text
            })

if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE)
pd.DataFrame(combined_data).to_csv(OUTPUT_FILE, index=False)
print(f"✅ Saved YouTube data: {OUTPUT_FILE}")
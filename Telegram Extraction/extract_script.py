import os
import re
import json
import shutil
from datetime import datetime, timedelta
from telethon.sync import TelegramClient

# ---------- USER CONFIGURATION ------------
API_ID = "API_ID_HERE"
API_HASH = "API_HASH_HERE"
LINKS_FILE = "links.txt"
EXPORT_FOLDER = "script_exports"
MODE = "date_range"        # Options: "last_n", "date_range", "since_date"
LAST_N = 3                 # Only for "last_n" mode
PERIOD_TYPE = "weeks"      # "days", "weeks", "months"
START_DATE = datetime(2025, 2, 12)
END_DATE = datetime(2025, 4, 1)    # Only for "date_range"
DOWNLOAD_TYPES = []        # Example: ["photo", "video", "audio", "files"]
LINK_MODE = "remove"       # "numbered", "remove", "original"
MAX_MESSAGES = 6000        # Max messages per channel

# ---------- SIMPLE FUNCTIONS -------------
def read_links(filename):
    """Read links from a text file."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return []

def extract_username(link):
    """Convert a Telegram channel link to @username format."""
    if "t.me" in link:
        return "@" + link.split("/")[-1].replace('+', '')
    return link

def create_channel_folders(channel):
    """Create folders for exporting text and media."""
    base = os.path.join(EXPORT_FOLDER, channel[1:])
    text_dir = os.path.join(base, "text_export")
    media_dir = os.path.join(base, "media")
    os.makedirs(text_dir, exist_ok=True)
    os.makedirs(os.path.join(text_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(text_dir, "js"), exist_ok=True)
    for sub in ["photo", "video", "audio", "files"]:
        os.makedirs(os.path.join(media_dir, sub), exist_ok=True)
    return text_dir, media_dir

def copy_static_files(text_dir):
    """Copy static files (style.css, script.js) if present."""
    for fname in ["style.css", "script.js"]:
        if os.path.exists(fname):
            shutil.copy(fname, os.path.join(text_dir, fname))

def download_media(message, media_dir):
    paths, types = [], {}
    if "photo" in DOWNLOAD_TYPES and message.photo:
        path = message.download_media(file=os.path.join(media_dir, "photo", f"photo_{message.id}.jpg"))
        paths.append(path)
        types["Photo"] = types.get("Photo", 0) + 1
    if "video" in DOWNLOAD_TYPES and message.video:
        path = message.download_media(file=os.path.join(media_dir, "video", f"video_{message.id}.mp4"))
        paths.append(path)
        types["Video"] = types.get("Video", 0) + 1
    if "files" in DOWNLOAD_TYPES and message.document:
        path = message.download_media(file=os.path.join(media_dir, "files", f"file_{message.id}.pdf"))
        paths.append(path)
        types["File"] = types.get("File", 0) + 1
    if "audio" in DOWNLOAD_TYPES and message.voice:
        path = message.download_media(file=os.path.join(media_dir, "audio", f"voice_{message.id}.ogg"))
        paths.append(path)
        types["Audio"] = types.get("Audio", 0) + 1
    return paths, types

def process_links(text, link_mode):
    link_pattern = r"\[([^\]]+)\]\((https?://[^\s]+)\)"
    embedded_links = re.findall(link_pattern, text)
    raw_links = re.findall(r"\bhttps?://[^\s)]+", text)
    embedded_video_links = []  # You can add logic for video links if needed

    if link_mode == "original":
        return text, [], [], []
    if link_mode == "numbered":
        for i, (word, link) in enumerate(embedded_links, start=1):
            text = text.replace(f"[{word}]({link})", f"{word}[{i}]")
        numbered_links = [f"[{i}] {link}" for i, (_, link) in enumerate(embedded_links, start=1)]
        return text, numbered_links, raw_links, embedded_video_links
    if link_mode == "remove":
        text = re.sub(link_pattern, r"\1", text)
        text = re.sub(r"https?://[^\s]+", "", text).strip()
        return text, [], [], embedded_video_links
    return text, [], raw_links, embedded_video_links

def compute_date_range(mode, last_n, period_type, start_date, end_date):
    today = datetime.today()
    if mode == "last_n":
        if period_type == "days":
            date_from = today - timedelta(days=last_n)
        elif period_type == "weeks":
            date_from = today - timedelta(weeks=last_n)
        elif period_type == "months":
            new_month = today.month - last_n if today.month > last_n else 12 - (last_n - today.month)
            date_from = today.replace(month=new_month)
        else:
            date_from = today
        date_to = today
    elif mode == "date_range":
        date_from = start_date
        date_to = end_date
    elif mode == "since_date":
        date_from = start_date
        date_to = today
    else:
        raise ValueError("Invalid mode")
    return date_from, date_to

# ---------- MAIN SCRIPT ---------------
if __name__ == "__main__":
    print("Starting Telegram export script...")

    links = read_links(LINKS_FILE)
    if not links:
        print("No channel links found, exiting.")
        exit(1)

    channels = [extract_username(link) for link in links]
    date_from, date_to = compute_date_range(MODE, LAST_N, PERIOD_TYPE, START_DATE, END_DATE)
    exported_channels = 0

    with TelegramClient("session", API_ID, API_HASH) as client:
        print("Logged in to Telegram.")

        for channel in channels:
            print(f"\n--- Processing {channel} ---")
            try:
                entity = client.get_entity(channel)
            except Exception as e:
                print(f"  Error: cannot find channel {channel} ({e})")
                continue

            text_dir, media_dir = create_channel_folders(channel)
            messages_data, text_content = [], []

            # Check if there are messages
            if not client.get_messages(channel, limit=1):
                print(f"  No messages in {channel}")
                continue

            print(f"  Collecting messages from {date_from.strftime('%d-%m-%Y')} to {date_to.strftime('%d-%m-%Y')}")
            all_messages = client.get_messages(channel, limit=MAX_MESSAGES)
            for msg in all_messages:
                msg_date = msg.date.replace(tzinfo=None)
                if not (date_from <= msg_date <= date_to):
                    continue

                text, numbered_links, raw_links, embedded_video_links = process_links(msg.text if msg.text else "<No text>", LINK_MODE)
                media_paths, media_types = download_media(msg, media_dir)
                media_str = ", ".join([f"{k} - {v}" for k, v in media_types.items()]) if media_types else "No media"

                post = f"{msg_date.strftime('%d-%m-%Y %H:%M')}\n"
                post += f"Media: {media_str}\n"
                if embedded_video_links:
                    post += f"Embedded Video Links: {', '.join(embedded_video_links)}\n"
                if raw_links and not embedded_video_links:
                    post += f"Links: {', '.join(raw_links)}\n"
                post += text
                if numbered_links:
                    post += "\n" + "\n".join(numbered_links)
                post += "\n-----SPLITTER-----\n\n"
                text_content.append(post)

                if text and text.strip() != "<No text>":
                    messages_data.append({"date": msg_date.strftime('%d-%m-%Y %H:%M'), "text": text})

            # Save messages to files
            text_content.reverse()
            with open(os.path.join(text_dir, "messages.txt"), "w", encoding="utf-8") as tf:
                tf.write("\n".join(text_content))

            if messages_data:
                with open(os.path.join(text_dir, "messages.json"), "w", encoding="utf-8") as jf:
                    json.dump({"channel": channel, "messages": messages_data}, jf, indent=4, ensure_ascii=False)
                print(f"  Exported {len(messages_data)} messages for {channel}")
            else:
                print(f"  No text messages for {channel} in the given range.")

            copy_static_files(text_dir)
            exported_channels += 1

    print(f"\nAll done! Exported data for {exported_channels} channels to '{EXPORT_FOLDER}'.")


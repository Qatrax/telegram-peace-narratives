# Telegram Channel Export Script

This script downloads and exports posts (including text and media) from a list of Telegram channels using the Telethon Python library.
It saves all posts within a specified date range (or other modes) to readable .txt and .json files, along with optional media (photos, videos, audio, files) for each channel.

## Features

* Export text and media from public Telegram channels. 
* Filter messages by date range or relative period (e.g. last 2 weeks).
* Structured folder export: each channel in its own folder, with subfolders for text, CSS/JS, and media types.
* Link processing modes: remove links, number links, or keep them as is.
* Customizable download settings.

## Requirements
* Python 3.8+
* Telethon

Install dependencies:

```bash
pip install telethon
```


## Setup

1. #### Clone or download the script.
2. #### Get your Telegram API credentials:
* Sign up at https://my.telegram.org.
* Go to API development tools and create an application to get your API_ID and API_HASH.

3. #### Prepare your channels list:
* Create a links_new.txt file with one Telegram channel link per line (example: https://t.me/examplechannel).
4. #### (Optional)
* Place your style.css and script.js files in the same directory if you want them to be copied to each export.

## Configuration

All main settings are at the top of the script:

```python API_ID = "API_ID_HERE"         # your Telegram API ID API_HASH = "API_HASH_HERE"     # your Telegram API hash
LINKS_FILE = "links_new.txt"   # file with channel links
EXPORT_FOLDER = "script_exports"
MODE = "date_range"            # "last_n", "date_range", "since_date"
LAST_N = 3                     # number of periods (for "last_n" mode)
PERIOD_TYPE = "weeks"          # "days", "weeks", or "months"
START_DATE = datetime(2025, 2, 12)
END_DATE = datetime(2025, 4, 1)   # for "date_range" mode

DOWNLOAD_TYPES = []            # e.g. ["photo", "video", "audio", "files"]
LINK_MODE = "remove"           # "numbered", "remove", "original"
MAX_MESSAGES = 6000            # maximum number of messages per channel
```

* #### MODE:
  * `"date_range"`: set `START_DATE` and `END_DATE`
  * `"last_n"`: download for last N periods (days/weeks/months)
  * `"since_date"`: download from `START_DATE` until today

* #### DOWNLOAD_TYPES:
  * Add any of: "photo", "video", "audio", "files" to also download these media types. If empty - just text

* #### LINK_MODE:
  * `"remove"`: removes all links
  * `"numbered"`: replaces links with [1], [2], ...
  * `"original"`: leaves links as-is

## Running the Script
```bash
python telegram_export.py
```
When prompted, the script will ask for your Telegram code for login (first launch only).

## Output
* All exported data is saved to the folder specified in `EXPORT_FOLDER` (default: `script_exports`).
* Each channel gets its own subfolder:
```css
script_exports/
  channel1/
    text_export/
      messages.txt
      messages.json
      style.css (if provided)
      script.js (if provided)
    media/
      photo/
      video/
      audio/
      files/
  channel2/
    ...
```
* messages.txt contains a readable dump of all posts.
* messages.json contains the same messages in structured JSON format (date + text).

## Troubleshooting
* Make sure your `API_ID` and `API_HASH` are correct.
* Only public channels (or those you have access to) can be exported.
* If you see errors about missing modules, make sure telethon is installed and you are using Python 3.8+.

## License
MIT License.

## Credits
Author: Egor Kozhevnikov, Charles University, 2025
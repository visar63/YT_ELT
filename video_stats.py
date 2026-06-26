import requests
import sys
import json
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

CHANNEL_HANDLE = "MrBeast"

URL = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

def get_channel_playlist_id():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    data = response.json()
    channel_playlist_Id = data["items"][0]["contentDetails"]["relatedPlaylists"]['uploads']
    # json_data = json.dumps(data, indent=4)
    return channel_playlist_Id

def main():
    try:
        print(get_channel_playlist_id())
        return 0 # Success
    except requests.RequestException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1 # Error


if __name__ == "__main__":
    raise SystemExit(main())

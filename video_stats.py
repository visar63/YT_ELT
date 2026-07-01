import requests
import sys
import json
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHANNEL_HANDLE = "MrBeast"
MAX_RESULTS = 50


URL = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}"

def get_channel_playlist_id():
    response = requests.get(URL, timeout=30)
    response.raise_for_status()

    data = response.json()
    channel_playlist_Id = data["items"][0]["contentDetails"]["relatedPlaylists"]['uploads']
    # json_data = json.dumps(data, indent=4)
    # print(f'Channel Playlist ID: {channel_playlist_Id}')
    return channel_playlist_Id

def get_video_Ids(playlist_id):
    video_ids = []
    page_token = None

    url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={MAX_RESULTS}&playlistId={playlist_id}&key={API_KEY}"
    while True:
        if page_token:
            url += f"&pageToken={page_token}"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        video_ids.extend([item["contentDetails"]["videoId"] for item in data["items"]])
        page_token = data.get("nextPageToken")
        # print(f"Next page token: {page_token}")
        if not page_token:
            break
    return video_ids

def batch_list(video_ids, batch_size=50):
    for i in range(0, len(video_ids), batch_size):
        yield video_ids[i:i + batch_size] # Yield batches of video IDs, each of size `batch_size`

def get_video_details(video_ids):
    extracted_data = []
    for batch in batch_list(video_ids):
        video_ids_str = ','.join(batch)

        url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"

        # print(f"Fetching video details for batch: {batch}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()
        for item in data["items"]:
            extracted_data.append({
                "video_id": item["id"],
                "publishedAt":  item["snippet"]["publishedAt"],
                "title":        item["snippet"]["title"],
                "duration":     item["contentDetails"]["duration"],
                "viewCount":    item["statistics"].get("viewCount", None),
                "likeCount":    item["statistics"].get("likeCount", None),
                "commentCount": item["statistics"].get("commentCount", None)
            })
        # extracted_data.extend([item["snippet"] for item in data["items"]])
    return extracted_data

def save_to_json(data, filename):
    filepath = f"data/{filename}"
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():

    #check if folder 'data' exists, if not create it
    if not os.path.exists("data"):
        os.makedirs("data")

    try:
        playlist_id = get_channel_playlist_id()
        # print(f'Playlist ID: {playlist_id}')

        video_ids = get_video_Ids(playlist_id)
        # print(f'Video IDs: {video_ids}')

        video_details = get_video_details(video_ids)
        # print(f'Video Details: {video_details}')
        save_to_json(video_details, f"video_details_{date.today()}.json")

    except requests.RequestException as exc:
        print(f"Error: {exc}", file=sys.stderr)
        # return 1 # Error

if __name__ == "__main__":
    raise SystemExit(main())

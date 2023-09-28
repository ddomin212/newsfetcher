import re
from datetime import datetime, timedelta

import googleapiclient.discovery
from google.oauth2 import service_account
from langchain.document_loaders import YoutubeLoader

# Set up the API client
api_key = "AIzaSyD91OGsIihNZErxJcN-_Z2srudr7T1Oe2c"
service = googleapiclient.discovery.build(
    "youtube", "v3", developerKey=api_key
)


def get_transcript(video_id):
    loader = YoutubeLoader.from_youtube_url(
        f"https://www.youtube.com/watch?v={video_id}",
        language="en",
    )
    transcript = loader.load()
    return transcript


def get_videos_last_week(channel_id, videos):
    one_day_ago = (datetime.now() - timedelta(days=1)).isoformat() + "Z"

    request = service.search().list(
        channelId=channel_id,
        part="snippet",
        type="video",
        order="date",
        publishedAfter=one_day_ago,
    )

    response = request.execute()

    for item in response["items"]:
        video_title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        videos.append({"title": video_title, "id": video_id})


def get_channel_id(channel_url):
    match = re.search(r"/@([\w-]+)/", channel_url)
    if match:
        username = match.group(1)
        search_response = (
            service.search()
            .list(
                q=username,
                type="channel",
                part="id",
                maxResults=1,
            )
            .execute()
        )

        channel_id = search_response["items"][0]["id"]["channelId"]

        return channel_id
    return None


def get_videos():
    # Example channel URL
    channel_urls = [
        "https://www.youtube.com/@MattVidPro/videos",
        "https://www.youtube.com/@airevolutionx/videos",
        "https://www.youtube.com/@aiexplained-official/videos",
        "https://www.youtube.com/@matthew_berman/videos",
        "https://www.youtube.com/@mreflow/videos",
        "https://www.youtube.com/@1littlecoder/videos",
    ]

    videos = []
    for url in channel_urls:
        channel_id = get_channel_id(url)
        get_videos_last_week(channel_id, videos)

    # print(len(videos))

    corpora = ""
    docs = []
    for video in videos:
        doc = get_transcript(video["id"])
        # print(len(doc))
        docs.append(doc[0].page_content)
        corpora += doc[0].page_content + ". "

    return corpora

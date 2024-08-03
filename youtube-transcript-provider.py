"""
title: Youtube Transcript Provider
description: A tool that returns the full, detailed youtube transcript in English of a passed in youtube url.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.1
license: MIT
"""

import requests

import unittest
import re

def get_youtube_video_id(url: str):
    match = re.search(r'(?:v=|be/|watch\?v=)([^&?]+)', url)
    if match:
        return match.group(1)
    else:
        return None
    
def get_best_transcript(transcripts_dict: dict) -> list[str]:
    if "en" in transcripts_dict:
        return transcripts_dict["en"]["auto"]
    elif "en_auto" in transcripts_dict:
        return transcripts_dict["en_auto"]["auto"]
    else:
        return []
    

class Tools:
    def __init__(self):
        pass

    def get_youtube_transcript(self, url: str) -> str:
        """
        Provides the title and full transcript of a YouTube video in English.

        :param url: The URL of the youtube video that you want the transcript for.
        :return: The title and full transcript of the YouTube video in English.
        """

        video_id = get_youtube_video_id(url)
        if video_id is None:
            return f"Error: Invalid YouTube URL: {url}"
        
        notegpt_url = f"https://notegpt.io/api/v1/get-transcript-v2?video_id={video_id}&platform=youtube"
        response = requests.get(notegpt_url)

        # Check if the request was successful
        if response.status_code != 200 and response.headers.get("Content-Type") != "application/json":
            return f"Error: Failed to get transcript. Status code: {response.status_code} - {response.text}"
        
        # Parse the JSON response
        json_content = response.json()
        if json_content["code"] != 100000:
            return f"Error: {json_content['message']}"

        title = json_content["data"]["videoInfo"]["name"]
        transcript = get_best_transcript(json_content["data"]["transcripts"])
        if len(transcript) == 0:
            return f"Error: Failed to find english transcript. Available languages: {json_content['data']['transcripts'].keys()}"
        
        text_only_transcript = " ".join([caption['text'] for caption in transcript])

        return f"Title: {title}\n\nTranscript:\n{text_only_transcript}"
        

class YoutubeTranscriptProviderTest(unittest.TestCase):

    def test_short_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(get_youtube_video_id(url), "dQw4w9WgXcQ")

    def test_long_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=5s"
        self.assertEqual(get_youtube_video_id(url), "dQw4w9WgXcQ")

    def test_short_url_with_timestamps(self):
        url = "https://youtu.be/dQw4w9WgXcQ?t=5s"
        self.assertEqual(get_youtube_video_id(url), "dQw4w9WgXcQ")

    def test_invalid_url(self):
        url = "https://www.example.com/invalid"
        self.assertIsNone(get_youtube_video_id(url))

    def test_get_youtube_transcript(self):
        url = "https://www.youtube.com/watch?v=zmP9bZANSaM"
        self.assertEqual(len(Tools().get_youtube_transcript(url)), 1384)

    def test_get_youtube_transcript_with_invalid_url(self):
        url = "https://www.example.com/invalid"
        self.assertEqual(Tools().get_youtube_transcript(url), f"Error: Invalid YouTube URL: {url}")

    def test_get_youtube_transcript_with_invalid_video_id(self):
        url = "https://www.youtube.com/watch?v=zhWDdy_5v3w"
        self.assertEqual(Tools().get_youtube_transcript(url), f"Error: no transcript")

if __name__ == '__main__':
    unittest.main()
"""
title: Youtube Transcript Provider
description: A tool that returns the full, detailed youtube transcript in English of a passed in youtube url.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.5
license: MIT
"""

import requests
import re
from typing import Callable, Any

import unittest

def get_youtube_video_id(url: str):
    if url is None or len(url) == 0:
        return None
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
    
class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def progress_update(self, description):
        await self.emit(description)

    async def error_update(self, description):
        await self.emit(description, "error", True)

    async def success_update(self, description):
        await self.emit(description, "success", True)

    async def emit(self, description="Unknown State", status="in_progress", done=False):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )
    

class Tools:
    def __init__(self):
        pass

    async def get_youtube_transcript(self, url: str, __event_emitter__: Callable[[dict], Any] = None) -> str:
        """
        Provides the title and full transcript of a YouTube video in English.
        Only use if the user supplied a valid YouTube URL.
        Examples of valid YouTube URLs: https://youtu.be/dQw4w9WgXcQ, https://www.youtube.com/watch?v=dQw4w9WgXcQ

        :param url: The URL of the youtube video that you want the transcript for.
        :return: The title and full transcript of the YouTube video in English, or an error message.
        """
        emitter = EventEmitter(__event_emitter__)


        try:
            await emitter.progress_update(f"Getting transcript for {url}")
            video_id = get_youtube_video_id(url)
            error_message = f"Error: Invalid YouTube URL: {url}"
            if video_id is None:
                await emitter.error_update(error_message)
                return error_message
            elif video_id == "dQw4w9WgXcQ": # LLM's love passing in this url when the user doesn't provide one
                await emitter.error_update(f"Error: No URL provided (except for Rick Roll ... is that what you want?).")
                return error_message
            
            notegpt_url = f"https://notegpt.io/api/v1/get-transcript-v2?video_id={video_id}&platform=youtube"
            response = requests.get(notegpt_url)

            # Check if the request was successful
            if response.status_code != 200 and response.headers.get("Content-Type") != "application/json":
                error_message = f"Error: Failed to get transcript. Status code: {response.status_code} - {response.text}"
                await emitter.error_update(error_message)
                return error_message
            
            # Parse the JSON response
            json_content = response.json()
            if json_content["code"] != 100000:
                error_message = f"Error: {json_content['message']}"
                await emitter.error_update(error_message)
                return error_message

            title = json_content["data"]["videoInfo"]["name"]
            transcript = get_best_transcript(json_content["data"]["transcripts"])
            if len(transcript) == 0:
                error_message = f"Error: Failed to find english transcript. Available languages: {json_content['data']['transcripts'].keys()}"
                await emitter.error_update(error_message)
                return error_message
            
            text_only_transcript = " ".join([caption['text'] for caption in transcript])
            await emitter.success_update(f"Transcript for {title} retrieved!")
            return f"Title: {title}\n\nTranscript:\n{text_only_transcript}"

        except Exception as e:
            error_message = f"Error: {str(e)}"
            await emitter.error_update(error_message)
            return error_message


class YoutubeIdExtractorTest(unittest.TestCase):
    def test_url(self):
        short_url = "https://youtu.be/dQw4w9WgXcQ"
        long_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(get_youtube_video_id(short_url), "dQw4w9WgXcQ")
        self.assertEqual(get_youtube_video_id(long_url), "dQw4w9WgXcQ")

    def test_url_with_timestamps(self):
        short_url = "https://youtu.be/dQw4w9WgXcQ?t=5s"
        long_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=5s"
        self.assertEqual(get_youtube_video_id(short_url), "dQw4w9WgXcQ")
        self.assertEqual(get_youtube_video_id(long_url), "dQw4w9WgXcQ")

    def test_invalid_url(self):
        invalid_url = "https://www.example.com/invalid"
        self.assertIsNone(get_youtube_video_id(invalid_url))
        self.assertIsNone(get_youtube_video_id(None))
        self.assertIsNone(get_youtube_video_id(""))

class YoutubeTranscriptProviderTest(unittest.IsolatedAsyncioTestCase):
    async def assert_transcript_length(self, url: str, expected_length: int):
        self.assertEqual(len(await Tools().get_youtube_transcript(url)), expected_length)

    async def assert_transcript_error(self, url: str):
        response = await Tools().get_youtube_transcript(url)
        self.assertTrue("Error" in response)

    async def test_get_youtube_transcript(self):
        url = "https://www.youtube.com/watch?v=zhWDdy_5v2w"
        await self.assert_transcript_length(url, 1384)

    async def test_get_youtube_transcript_with_invalid_url(self):
        invalid_url = "https://www.example.com/invalid"
        missing_url = "https://www.youtube.com/watch?v=zhWDdy_5v3w"

        await self.assert_transcript_error(invalid_url)
        await self.assert_transcript_error(missing_url)

    async def test_get_youtube_transcript_with_none_arg(self):
        await self.assert_transcript_error(None)
        await self.assert_transcript_error("")

if __name__ == '__main__':
    print("Running tests...")
    unittest.main()
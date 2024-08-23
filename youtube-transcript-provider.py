"""
title: Youtube Transcript Provider
description: A tool that returns the full, detailed youtube transcript in English of a passed in youtube url.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.6
license: MIT
"""

import unittest
from typing import Callable, Any

from langchain_community.document_loaders import YoutubeLoader
from pydantic import BaseModel, Field


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
                {"type": "status", "data": {"status": status, "description": description, "done": done, }, })


class Tools:
    class Valves(BaseModel):
        TRANSCRIPT_LANGUAGE: str = Field(default="en,en_auto",
                                         description="A comma-separated list of languages from highest priority to lowest.", )
        TRANSCRIPT_TRANSLATE: str = Field(default="en",
                                          description="The language you want the transcript to auto-translate to, if it does not already exist.", )
        CITITATION: bool = Field(default="True", description="True or false for citation", )

    def __init__(self):
        self.valves = self.Valves()
        self.citation = self.valves.CITITATION

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

            error_message = f"Error: Invalid YouTube URL: {url}"
            if not url or url == "":
                await emitter.error_update(error_message)
                return error_message
            elif ("dQw4w9WgXcQ" in url):  # LLM's love passing in this url when the user doesn't provide one
                await emitter.error_update(f"Error: No URL provided (except for Rick Roll ... is that what you want?).")
                return error_message

            languages = [item.strip() for item in self.valves.TRANSCRIPT_LANGUAGE.split(',')]
            transcript = YoutubeLoader.from_youtube_url(url, add_video_info=True, language=languages,
                                                        translation=self.valves.TRANSCRIPT_TRANSLATE).load()

            if len(transcript) == 0:
                error_message = f"Error: Failed to find transcript for {url}"
                await emitter.error_update(error_message)
                return error_message

            title = transcript[0].metadata["title"]
            transcript = "\n".join([document.page_content for document in transcript])

            await emitter.success_update(f"Transcript for {title} retrieved!")
            return f"Title: {title}\n\nTranscript:\n{transcript}"

        except Exception as e:
            error_message = f"Error: {str(e)}"
            await emitter.error_update(error_message)
            return error_message


class YoutubeTranscriptProviderTest(unittest.IsolatedAsyncioTestCase):
    async def assert_transcript_length(self, url: str, expected_length: int):
        self.assertEqual(len(expected_length, await Tools().get_youtube_transcript(url)))

    async def assert_transcript_error(self, url: str):
        response = await Tools().get_youtube_transcript(url)
        self.assertTrue("Error" in response)

    async def test_get_youtube_transcript(self):
        url = "https://www.youtube.com/watch?v=zhWDdy_5v2w"
        await self.assert_transcript_length(url, 1384)

    async def test_get_youtube_transcript_de(self):
        url = "https://www.youtube.com/watch?v=zhWDdy_5v2w"
        tools_instance = Tools()
        tools_instance.valves.TRANSCRIPT_TRANSLATE = "it"

        transcript_response = await tools_instance.get_youtube_transcript(url)
        self.assertEqual(1473, len(transcript_response))

    async def test_get_youtube_transcript_with_invalid_url(self):
        invalid_url = "https://www.example.com/invalid"
        missing_url = "https://www.youtube.com/watch?v=zhWDdy_5v3w"
        rick_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

        await self.assert_transcript_error(invalid_url)
        await self.assert_transcript_error(missing_url)
        await self.assert_transcript_error(rick_url)

    async def test_get_youtube_transcript_with_none_arg(self):
        await self.assert_transcript_error(None)
        await self.assert_transcript_error("")


if __name__ == "__main__":
    print("Running tests...")
    unittest.main()

"""
title: Enhanced Web Scrape
description: An improved web scraping tool that extracts text content using Jina Reader, now with better filtering, user-configuration, and UI feedback using emitters.
author: ekatiyar
author_url: https://github.com/ekatiyar
github: https://github.com/ekatiyar/open-webui-tools
original_author: Pyotr Growpotkin
original_author_url: https://github.com/christ-offer/
original_github: https://github.com/christ-offer/open-webui-tools
funding_url: https://github.com/open-webui
version: 0.0.3
license: MIT
"""

import requests
from typing import Callable, Any
import re
from pydantic import BaseModel, Field

import unittest

def extract_title(text):
  """
  Extracts the title from a string containing structured text.

  :param text: The input string containing the title.
  :return: The extracted title string, or None if the title is not found.
  """
  match = re.search(r'Title: (.*)\n', text)
  return match.group(1).strip() if match else None

def clean_urls(text) -> str:
    """
    Cleans URLs from a string containing structured text.

    :param text: The input string containing the URLs.
    :return: The cleaned string with URLs removed.
    """
    return re.sub(r'\((http[^)]+)\)', '', text)

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
    class Valves(BaseModel):
        DISABLE_CACHING: bool = Field(
            default=False, description="Bypass Jina Cache when scraping"
        )
        GLOBAL_JINA_API_KEY: str = Field(
            default="",
            description="(Optional) Jina API key. Allows a higher rate limit when scraping. Used when a User-specific API key is not available."
        )

    class UserValves(BaseModel):
        CLEAN_CONTENT: bool = Field(
            default=True, description="Remove links and image urls from scraped content. This reduces the number of tokens."
        )
        JINA_API_KEY: str = Field(
            default="",
            description="(Optional) Jina API key. Allows a higher rate limit when scraping."
        )

    def __init__(self):
        self.valves = self.Valves()

    async def web_scrape(self, url: str, __event_emitter__: Callable[[dict], Any] = None, __user__: dict = {}) -> str:
        """
        Scrape and process a web page using r.jina.ai

        :param url: The URL of the web page to scrape.
        :return: The scraped and processed webpage content, or an error message.
        """
        emitter = EventEmitter(__event_emitter__)

        await emitter.progress_update(f"Scraping {url}")
        jina_url = f"https://r.jina.ai/{url}"

        headers = {
            "X-No-Cache": "true" if self.valves.DISABLE_CACHING else "false",
            "X-With-Generated-Alt": "true",
        }

        if "valves" in __user__ and __user__["valves"].JINA_API_KEY:
            headers["Authorization"] = f"Bearer {__user__['valves'].JINA_API_KEY}"
        elif self.valves.GLOBAL_JINA_API_KEY:
            headers["Authorization"] = f"Bearer {self.valves.GLOBAL_JINA_API_KEY}"

        try:
            response = requests.get(jina_url, headers=headers)
            response.raise_for_status()

            should_clean = "valves" not in __user__ or __user__["valves"].CLEAN_CONTENT
            if should_clean:
                await emitter.progress_update("Received content, cleaning up ...")
            content = clean_urls(response.text) if should_clean else response.text

            title = extract_title(content)
            await emitter.success_update(f"Successfully Scraped {title if title else url}")
            return content

        except requests.RequestException as e:
            error_message = f"Error scraping web page: {str(e)}"
            await emitter.error_update(error_message)
            return error_message
        
class WebScrapeTest(unittest.IsolatedAsyncioTestCase):
    async def test_web_scrape(self):
        url = "https://toscrape.com/"
        content = await Tools().web_scrape(url)
        self.assertEqual("Scraping Sandbox", extract_title(content))
        self.assertEqual(len(content), 770)

if __name__ == "__main__":
    print("Running tests...")
    unittest.main()
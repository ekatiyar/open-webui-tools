# Open WebUI Tools

A collection of tools implemented to be used natively with [Open WebUI](https://github.com/open-webui/open-webui). Built using Python and leveraging the libraries provided in the Open WebUI environment.

## 🛠️ Tools

### 1. 🎞️ Youtube Transcript Provider
Provides a detailed, full-length transcript of any YouTube video in English.

#### Motivation
The native YouTube tool in Open WebUI employs RAG, which can hinder the model's ability to grasp the overall structure and logical flow of content, which impacts summarization performance negatively. This tool bypasses the RAG by providing the transcript directly to the model.

### 2. 🌐 Enhanced Web Scrape
An improved web scraping tool that extracts text content using Jina Reader, now with better filtering, user-configuration, and UI feedback using emitters. This tool is an improvement upon the [web scrape tool](https://github.com/christ-offer/open-webui-tools/blob/main/tools/web_scrape_jina.py) written by Pyotr Growpotkin.

#### Motivation
The original tool was missing some functionality I wanted, primarily in terms of providing feedback in Open WebUI when the tool was used, such as whether or not it was successfull. In the process of implementing that, I also explored Jina.ai's Reader API and fixed content filtering to reduce input size. Furthermore, I added configurability in the UI through Open WebUI's valves to allow configuration of content filtering and allow users to pass in their own Jina API key for higher rate limits.

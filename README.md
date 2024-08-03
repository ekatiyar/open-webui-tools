# Open WebUI Tools

A collection of tools implemented to be used natively with [Open WebUI](https://github.com/open-webui/open-webui). Built using Python and leveraging the libraries provided in the Open WebUI environment.

## 🛠️ Tools

### 1. Youtube Transcript Provider

Provides a detailed, full-length transcript of any YouTube video in English.

### Motivation
The native YouTube tool in Open WebUI employs RAG, which can hinder the model's ability to grasp the overall structure and logical flow of content, which impacts summarization performance negatively. This tool bypasses the RAG by providing the transcript directly to the model.
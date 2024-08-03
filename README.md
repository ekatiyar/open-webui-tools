# Open WebUI Tools

Some tools I have implemented to be used natively with [Open WebUI](https://github.com/open-webui/open-webui). Built with python with a focus on using provided python libraries in the Open WebUI environment.

# Tools

## Youtube Transcript Provider

Provides the full, detailed youtube transcript in English. 

### Motivation
The built-in youtube tool in Web UI uses RAG which negatively affects the ability of a model to understand the logical flow of a piece of content, which causes summarization performance to suffer. We provide that transcript to the model directly.

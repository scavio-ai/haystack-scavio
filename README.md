# scavio-haystack

[![PyPI - Version](https://img.shields.io/pypi/v/scavio-haystack.svg)](https://pypi.org/project/scavio-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scavio-haystack.svg)](https://pypi.org/project/scavio-haystack)

[Scavio](https://scavio.dev) integration for [Haystack](https://haystack.deepset.ai) by deepset.

Provides `ScavioWebSearch`, a web search component backed by the Scavio API. It returns results
as Haystack `Document` objects (with title and URL metadata) plus the list of source links, and
mirrors the existing `TavilyWebSearch` / `ExaWebSearch` components.

Scavio is a unified search API for AI agents. Get an API key at
[dashboard.scavio.dev](https://dashboard.scavio.dev).

## Installation

```bash
pip install scavio-haystack
```

## Usage

```python
from haystack_integrations.components.websearch.scavio import ScavioWebSearch
from haystack.utils import Secret

web_search = ScavioWebSearch(
    api_key=Secret.from_env_var("SCAVIO_API_KEY"),  # defaults to SCAVIO_API_KEY
    top_k=5,
)

result = web_search.run(query="What is Haystack by deepset?")
documents = result["documents"]
links = result["links"]
```

### In a pipeline

```python
from haystack import Pipeline
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

template = """
Given the following web search results, answer the question.

Results:
{% for doc in documents %}{{ doc.content }}
{% endfor %}

Question: {{ query }}
Answer:
"""

pipe = Pipeline()
pipe.add_component("search", ScavioWebSearch(top_k=5))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OpenAIGenerator())
pipe.connect("search.documents", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")

query = "What is Haystack by deepset?"
result = pipe.run(data={"search": {"query": query}, "prompt_builder": {"query": query}})
print(result["llm"]["replies"][0])
```

### Async support

```python
import asyncio
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

async def main():
    web_search = ScavioWebSearch(top_k=3)
    result = await web_search.run_async(query="What is Haystack by deepset?")
    print(f"Found {len(result['documents'])} documents")

asyncio.run(main())
```

## Parameters

- **`api_key`**: API key for Scavio. Defaults to the `SCAVIO_API_KEY` environment variable.
- **`top_k`**: Maximum number of results to return. Defaults to 10.
- **`search_params`**: Additional parameters for the Scavio Google (v2) search endpoint.
  Supported keys: `country_code` (mapped to `gl`), `language` (mapped to `hl`), `page`
  (mapped to `start=(page-1)*10`), `device`, and `nfpr`. Any other key is passed through
  verbatim (e.g. `google_domain`, `location`, `safe`). Can be set at init time or overridden
  per `run`.

## Development

This project uses [Hatch](https://hatch.pypa.io/).

```bash
pip install hatch

hatch run fmt-check     # lint + format check
hatch run test:unit     # unit tests
hatch run test:all      # all tests (set SCAVIO_API_KEY for integration tests)
```

## About Scavio

Scavio is a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents) that unifies a [Google Search API](https://scavio.dev/google-search-api), [Amazon Product API](https://scavio.dev/amazon-product-api), [Walmart Product API](https://scavio.dev/walmart-product-api), [YouTube API](https://scavio.dev/youtube-transcript-api), [Reddit API](https://scavio.dev/reddit-api), [TikTok API](https://scavio.dev/tiktok-api), and [Instagram API](https://scavio.dev/instagram-api) behind a single key, returning structured JSON with no scraping or proxies. Teams evaluating a [Tavily alternative](https://scavio.dev/alternatives/tavily) or [SerpAPI alternative](https://scavio.dev/alternatives/serpapi) get web search plus commerce and social data on one plan.

## License

`scavio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

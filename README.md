# scavio-haystack

[![PyPI - Version](https://img.shields.io/pypi/v/scavio-haystack.svg)](https://pypi.org/project/scavio-haystack)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/scavio-haystack.svg)](https://pypi.org/project/scavio-haystack)

[Scavio](https://scavio.dev) integration for [Haystack](https://haystack.deepset.ai) by deepset.

Provides `ScavioWebSearch`, a web search component backed by the Scavio API. It returns results
as Haystack `Document` objects (with title and URL metadata) plus the list of source links, and
mirrors the existing `TavilyWebSearch` / `ExaWebSearch` components.

Scavio is a unified search API for AI agents. Get an API key at
[dashboard.scavio.dev](https://dashboard.scavio.dev).

## Scope: 1 endpoint, by design

This package is a **curated subset** of the Scavio API, not a wrapper around all of it.
It exposes exactly **1** of Scavio's 195 endpoints:

| Component | Endpoint | Platform | Credits |
|---|---|---|---|
| `ScavioWebSearch` | `POST /api/v2/google` | Google (web search) | 1 |

That is the whole surface. A Haystack web search component has one job — turn a query into
`Document`s — and only Google web search maps onto it cleanly, so this package stays at one
endpoint on purpose rather than growing into a general-purpose API client.

**Credits:** 1 credit per `run` / `run_async` call. Nothing here touches the endpoints that
cost more (YouTube transcripts are 5, most Instagram calls are 2, a LinkedIn job is 30) or the
body-priced ones, whose cost is a function of the request rather than a flat number
(Walmart, Threads, Kuaishou and `extract`). A `ScavioWebSearch` pipeline is flat 1 credit
per search.

### Reaching the rest of the API

Scavio covers **195 live endpoints**: 194 across 31 platforms, plus `extract`, which reads
any URL. The platforms are **Google, YouTube, Amazon, Walmart, eBay, Target, Home Depot,
Reddit, X, TikTok, TikTok Shop, Instagram, LinkedIn, Threads, Kuaishou, Zillow, Redfin,
Booking.com, Tripadvisor, Airbnb, Yelp, Indeed, Glassdoor, the Apple App Store, Google Play,
SEC EDGAR, Companies House, G2, Capterra, Google Ads Transparency and the Meta Ad Library.**
The most recent batch added **93 endpoints across 22 platforms plus `extract`** — 21 of those
platforms are new to Scavio and Walmart was rebuilt. **None of them are reachable through this
package**, which stays at Google web search. Two ways to use them from Haystack:

- **Hosted MCP server** — `https://mcp.scavio.dev/mcp` exposes 191 tools, authenticated with
  an `x-api-key` header. No install; a curated subset loads by default and the rest is one
  env var away. See the [MCP docs](https://scavio.dev/docs/mcp).
- **The `scavio` SDK directly** — it is already a dependency of this package:
  `ScavioClient(api_key=...).youtube.transcript(...)`, `.ebay.search(...)`,
  `.sec.filings(...)`, `.meta_ads.search(...)`, and so on. Reading an arbitrary URL is a
  top-level method, not a namespace: `client.extract(url, format="markdown")`, never
  `client.extract.extract(...)`. Wrap what you need in your own Haystack component — see the
  [SDK reference](https://scavio.dev/docs/python-sdk-reference) and the
  [full endpoint list](https://scavio.dev/docs/api-reference).

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

Scavio is a [search API for AI agents](https://scavio.dev/search-api-for-ai-agents) that unifies a [Google Search API](https://scavio.dev/google-search-api), [Amazon Product API](https://scavio.dev/amazon-product-api), [Walmart Product API](https://scavio.dev/walmart-product-api), [YouTube API](https://scavio.dev/youtube-transcript-api), [Reddit API](https://scavio.dev/reddit-api), [TikTok API](https://scavio.dev/tiktok-api), TikTok Shop, [Instagram API](https://scavio.dev/instagram-api), X, and LinkedIn behind a single key, returning structured JSON with no scraping or proxies. Teams evaluating a [Tavily alternative](https://scavio.dev/alternatives/tavily) or [SerpAPI alternative](https://scavio.dev/alternatives/serpapi) get web search plus commerce and social data on one plan.

The same key also reaches the newer verticals — [eBay sold-listing price history](https://scavio.dev/docs/ebay-search), [Target](https://scavio.dev/docs/target-search) and [Home Depot](https://scavio.dev/docs/home-depot-search), [Zillow](https://scavio.dev/docs/zillow-search) and [Redfin](https://scavio.dev/docs/redfin-search), [Booking.com](https://scavio.dev/docs/booking-search), [Tripadvisor](https://scavio.dev/docs/tripadvisor-search) and [Airbnb](https://scavio.dev/docs/airbnb-search), [Yelp](https://scavio.dev/docs/yelp-search), [Indeed](https://scavio.dev/docs/indeed-search) and [Glassdoor](https://scavio.dev/docs/glassdoor-companies), the [Apple App Store](https://scavio.dev/docs/app-store-search) and [Google Play](https://scavio.dev/docs/google-play-search), [G2](https://scavio.dev/docs/g2-search) and [Capterra](https://scavio.dev/docs/capterra-search), [Google Ads Transparency](https://scavio.dev/docs/google-ads-search) and the [Meta Ad Library](https://scavio.dev/docs/meta-ads-search), [SEC EDGAR](https://scavio.dev/docs/sec-edgar-filings) and [Companies House](https://scavio.dev/docs/companies-house-search), [Threads](https://scavio.dev/docs/threads-profile) and [Kuaishou](https://scavio.dev/docs/kuaishou-profile) — plus [Extract](https://scavio.dev/docs/extract), which turns any URL into HTML, Markdown or text. None of these ship as Haystack components here; use the MCP server or the SDK as described above.

New accounts get 50 one-time signup credits (no monthly refill, no credit card).

## License

`scavio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

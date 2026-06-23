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
- **`search_params`**: Additional parameters passed to the Scavio Google search endpoint.
  Supported keys include `country_code`, `language`, `page`, `search_type`, `device`, `nfpr`,
  `light_request`. Can be set at init time or overridden per `run`.

## Development

This project uses [Hatch](https://hatch.pypa.io/).

```bash
pip install hatch

hatch run fmt-check     # lint + format check
hatch run test:unit     # unit tests
hatch run test:all      # all tests (set SCAVIO_API_KEY for integration tests)
```

## License

`scavio-haystack` is distributed under the terms of the [Apache-2.0](https://spdx.org/licenses/Apache-2.0.html) license.

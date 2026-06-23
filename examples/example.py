# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

# Minimal example: search the web with Scavio and inspect the returned Documents.
# Export your key first:  export SCAVIO_API_KEY=sk_live_your_key
from haystack_integrations.components.websearch.scavio import ScavioWebSearch

web_search = ScavioWebSearch(top_k=5)

result = web_search.run(query="What is Haystack by deepset?")
for doc in result["documents"]:
    print(doc.meta["title"], "-", doc.meta["url"])

print(result["links"])

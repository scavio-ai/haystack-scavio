# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal

from haystack import component, logging
from haystack.utils import Secret

from scavio import AsyncScavioClient, ScavioClient

logger = logging.getLogger(__name__)


@component
class ScavioDecathlonSearch:
    """
    Search Decathlon products via the Scavio API.

    Supports 7 country domains: FR, ES, IT, IN, UK, PT and NET (international).

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioDecathlonSearch
    from haystack.utils import Secret

    search = ScavioDecathlonSearch(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = search.run(query="running shoes", country="fr")
    ```
    """

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("SCAVIO_API_KEY"),
    ) -> None:
        self.api_key = api_key
        self._client: ScavioClient | None = None
        self._async_client: AsyncScavioClient | None = None

    def warm_up(self) -> None:
        if self._client is None:
            self._client = ScavioClient(api_key=self.api_key.resolve_value())
        if self._async_client is None:
            self._async_client = AsyncScavioClient(api_key=self.api_key.resolve_value())

    @component.output_types(results=dict)
    def run(
        self,
        query: str,
        country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = "fr",
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        Search Decathlon products across 7 country domains.

        :param query: Product search query.
        :param country: Country domain.
        :param page: Results page, 1-based.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        response = self._client.decathlon.search(query, country=country, **params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        query: str,
        country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = "fr",
        page: int | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        response = await self._async_client.decathlon.search(query, country=country, **params)
        return {"results": response}


@component
class ScavioDecathlonProduct:
    """
    Get full Decathlon product details via the Scavio API.

    Supports 7 country domains: FR, ES, IT, IN, UK, PT and NET (international).

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioDecathlonProduct
    from haystack.utils import Secret

    product = ScavioDecathlonProduct(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = product.run(country="fr", product_url="https://www.decathlon.fr/p/...")
    ```
    """

    def __init__(
        self,
        api_key: Secret = Secret.from_env_var("SCAVIO_API_KEY"),
    ) -> None:
        self.api_key = api_key
        self._client: ScavioClient | None = None
        self._async_client: AsyncScavioClient | None = None

    def warm_up(self) -> None:
        if self._client is None:
            self._client = ScavioClient(api_key=self.api_key.resolve_value())
        if self._async_client is None:
            self._async_client = AsyncScavioClient(api_key=self.api_key.resolve_value())

    @component.output_types(results=dict)
    def run(
        self,
        country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = "fr",
        product_url: str | None = None,
        product_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get full details for a Decathlon product.

        :param country: Country domain.
        :param product_url: Full Decathlon product page URL (preferred).
        :param product_id: Decathlon numeric product ID.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if product_url is not None:
            params["product_url"] = product_url
        if product_id is not None:
            params["product_id"] = product_id
        response = self._client.decathlon.product(country=country, **params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        country: Literal["fr", "es", "it", "in", "uk", "pt", "net"] = "fr",
        product_url: str | None = None,
        product_id: str | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if product_url is not None:
            params["product_url"] = product_url
        if product_id is not None:
            params["product_id"] = product_id
        response = await self._async_client.decathlon.product(country=country, **params)
        return {"results": response}

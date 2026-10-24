# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from haystack import component, logging
from haystack.utils import Secret

from scavio import AsyncScavioClient, ScavioClient

logger = logging.getLogger(__name__)


@component
class ScavioKrogerSearch:
    """
    Search Kroger-family grocery products via the Scavio API.

    Kroger operates Kroger, Ralphs, Fred Meyer, Harris Teeter, King Soopers,
    Fry's and other banners.

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioKrogerSearch
    from haystack.utils import Secret

    search = ScavioKrogerSearch(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = search.run(query="organic eggs")
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
        page: int | None = None,
    ) -> dict[str, Any]:
        """
        Search Kroger-family stores for grocery products.

        :param query: Product search query.
        :param page: Results page, 1-based.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        response = self._client.kroger.search(query, **params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        query: str,
        page: int | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        response = await self._async_client.kroger.search(query, **params)
        return {"results": response}


@component
class ScavioKrogerProduct:
    """
    Get full Kroger product details via the Scavio API.

    Kroger operates Kroger, Ralphs, Fred Meyer, Harris Teeter, King Soopers,
    Fry's and other banners.

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioKrogerProduct
    from haystack.utils import Secret

    product = ScavioKrogerProduct(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = product.run(product_url="https://www.kroger.com/p/...")
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
        product_url: str | None = None,
        upc: str | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """
        Get full details for a Kroger product.

        :param product_url: Full Kroger product page URL (preferred).
        :param upc: Product UPC code.
        :param slug: Product URL slug.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if product_url is not None:
            params["product_url"] = product_url
        if upc is not None:
            params["upc"] = upc
        if slug is not None:
            params["slug"] = slug
        response = self._client.kroger.product(**params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        product_url: str | None = None,
        upc: str | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if product_url is not None:
            params["product_url"] = product_url
        if upc is not None:
            params["upc"] = upc
        if slug is not None:
            params["slug"] = slug
        response = await self._async_client.kroger.product(**params)
        return {"results": response}

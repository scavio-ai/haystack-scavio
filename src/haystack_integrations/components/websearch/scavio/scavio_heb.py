# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from haystack import component, logging
from haystack.utils import Secret

from scavio import AsyncScavioClient, ScavioClient

logger = logging.getLogger(__name__)


@component
class ScavioHebSearch:
    """
    Search HEB grocery products via the Scavio API.

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioHebSearch
    from haystack.utils import Secret

    search = ScavioHebSearch(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = search.run(query="organic milk")
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
        page_size: int | None = None,
        store_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Search HEB for grocery products.

        :param query: Product search query.
        :param page: Results page, 1-based.
        :param page_size: Results per page, 1-60. Defaults to 60.
        :param store_id: HEB store number from ScavioHebStores (store_number), e.g. "441".
            Prices, stock, aisle location and assortment come from that store; the store
            used is echoed in data.store {store_id, name}. US only. Omit for HEB's default store.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if store_id is not None:
            params["store_id"] = store_id
        response = self._client.heb.search(query, **params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        query: str,
        page: int | None = None,
        page_size: int | None = None,
        store_id: str | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page_size"] = page_size
        if store_id is not None:
            params["store_id"] = store_id
        response = await self._async_client.heb.search(query, **params)
        return {"results": response}


@component
class ScavioHebProduct:
    """
    Get full HEB product details via the Scavio API.

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioHebProduct
    from haystack.utils import Secret

    product = ScavioHebProduct(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = product.run(product_url="https://www.heb.com/product-detail/...")
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
        product_id: str | None = None,
        slug: str | None = None,
        store_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Get full details for an HEB product.

        :param product_url: Full HEB product page URL (preferred).
        :param product_id: HEB product id. Needs slug, unless store_id is set (then
            product_id alone works).
        :param slug: Product URL slug, required with product_id unless store_id is set.
        :param store_id: HEB store number from ScavioHebStores (store_number), e.g. "441".
            Price, stock and aisle location come from that store; the store used is echoed
            in data.store {store_id, name}. US only. Omit for HEB's default store.
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
        if slug is not None:
            params["slug"] = slug
        if store_id is not None:
            params["store_id"] = store_id
        response = self._client.heb.product(**params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        product_url: str | None = None,
        product_id: str | None = None,
        slug: str | None = None,
        store_id: str | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if product_url is not None:
            params["product_url"] = product_url
        if product_id is not None:
            params["product_id"] = product_id
        if slug is not None:
            params["slug"] = slug
        if store_id is not None:
            params["store_id"] = store_id
        response = await self._async_client.heb.product(**params)
        return {"results": response}


@component
class ScavioHebStores:
    """
    Find HEB store locations via the Scavio API.

    ### Usage example

    ```python
    from haystack_integrations.components.websearch.scavio import ScavioHebStores
    from haystack.utils import Secret

    stores = ScavioHebStores(api_key=Secret.from_env_var("SCAVIO_API_KEY"))
    result = stores.run(zip="78701")
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
        zip: str | None = None,
        city: str | None = None,
    ) -> dict[str, Any]:
        """
        Find HEB store locations.

        :param zip: 5-digit US ZIP code.
        :param city: City name.
        :returns: Dictionary with raw API response under 'results'.
        """
        if self._client is None:
            self.warm_up()
        assert self._client is not None
        params: dict[str, Any] = {}
        if zip is not None:
            params["zip"] = zip
        if city is not None:
            params["city"] = city
        response = self._client.heb.stores(**params)
        return {"results": response}

    @component.output_types(results=dict)
    async def run_async(
        self,
        zip: str | None = None,
        city: str | None = None,
    ) -> dict[str, Any]:
        if self._async_client is None:
            self.warm_up()
        assert self._async_client is not None
        params: dict[str, Any] = {}
        if zip is not None:
            params["zip"] = zip
        if city is not None:
            params["city"] = city
        response = await self._async_client.heb.stores(**params)
        return {"results": response}

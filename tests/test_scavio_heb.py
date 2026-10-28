# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

from unittest.mock import MagicMock

from haystack.utils import Secret

from haystack_integrations.components.websearch.scavio import ScavioHebProduct, ScavioHebSearch

OK = {"data": {"store": {"store_id": "441", "name": "Uvalde H-E-B"}}}


def test_heb_search_forwards_store_id():
    search = ScavioHebSearch(api_key=Secret.from_token("test-key"))
    search._client = MagicMock()
    search._client.heb.search.return_value = OK
    out = search.run(query="whole milk", store_id="441")
    search._client.heb.search.assert_called_once_with("whole milk", store_id="441")
    assert out["results"]["data"]["store"]["store_id"] == "441"


def test_heb_product_id_alone_with_store_id():
    product = ScavioHebProduct(api_key=Secret.from_token("test-key"))
    product._client = MagicMock()
    product._client.heb.product.return_value = OK
    product.run(product_id="314130", store_id="441")
    product._client.heb.product.assert_called_once_with(product_id="314130", store_id="441")


def test_heb_search_omits_store_id_when_unset():
    search = ScavioHebSearch(api_key=Secret.from_token("test-key"))
    search._client = MagicMock()
    search._client.heb.search.return_value = OK
    search.run(query="eggs")
    search._client.heb.search.assert_called_once_with("eggs")

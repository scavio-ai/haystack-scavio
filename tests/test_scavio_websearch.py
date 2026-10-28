# SPDX-FileCopyrightText: 2026-present Scavio <scavio.dev@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import re
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from haystack import Document
from haystack.core.serialization import component_from_dict, component_to_dict
from haystack.utils import Secret

from haystack_integrations.components.websearch.scavio import ScavioWebSearch

PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"
MINIMUM_SCAVIO = (0, 15, 0)


@pytest.mark.skipif(not PYPROJECT.is_file(), reason="pyproject.toml is only present in a source checkout.")
def test_scavio_floor_is_current():
    """The declared `scavio` floor must not fall behind the SDK the ecosystem assumes.

    A stale floor lets a resolver install an SDK without the current namespaces, so the
    package installs cleanly and then fails at import time in someone else's pipeline.
    """
    match = re.search(r'"scavio>=(\d+)\.(\d+)\.(\d+)"', PYPROJECT.read_text(encoding="utf-8"))
    assert match is not None, "pyproject.toml must pin a `scavio>=X.Y.Z` floor."
    assert tuple(int(part) for part in match.groups()) >= MINIMUM_SCAVIO


class TestScavioWebSearch:
    @pytest.fixture
    def search_response(self):
        return {
            "organic_results": [
                {"title": "Example Title", "link": "https://example.com", "snippet": "Example content", "position": 1}
            ]
        }

    @pytest.fixture
    def mock_client(self, search_response):
        client = MagicMock()
        client.google.search.return_value = search_response
        return client

    @pytest.fixture
    def mock_async_client(self, search_response):
        client = MagicMock()
        client.google.search = AsyncMock(return_value=search_response)
        return client

    def test_init_default(self, monkeypatch):
        monkeypatch.setenv("SCAVIO_API_KEY", "test-key")
        ws = ScavioWebSearch()
        assert ws.top_k == 10
        assert ws.search_params is None
        assert ws.api_key.resolve_value() == "test-key"

    def test_init_with_params(self):
        ws = ScavioWebSearch(
            api_key=Secret.from_token("custom-key"),
            top_k=5,
            search_params={"country_code": "us"},
        )
        assert ws.top_k == 5
        assert ws.search_params == {"country_code": "us"}

    def test_to_dict(self, monkeypatch):
        monkeypatch.setenv("SCAVIO_API_KEY", "test-key")
        ws = ScavioWebSearch(top_k=5, search_params={"country_code": "us"})
        data = component_to_dict(ws, "ScavioWebSearch")
        assert data["type"] == "haystack_integrations.components.websearch.scavio.scavio_websearch.ScavioWebSearch"
        assert data["init_parameters"]["top_k"] == 5
        assert data["init_parameters"]["search_params"] == {"country_code": "us"}

    def test_from_dict(self, monkeypatch):
        monkeypatch.setenv("SCAVIO_API_KEY", "test-key")
        data = {
            "type": "haystack_integrations.components.websearch.scavio.scavio_websearch.ScavioWebSearch",
            "init_parameters": {
                "top_k": 3,
                "search_params": {"language": "en"},
                "api_key": {"env_vars": ["SCAVIO_API_KEY"], "strict": True, "type": "env_var"},
            },
        }
        ws = component_from_dict(ScavioWebSearch, data, "ScavioWebSearch")
        assert ws.top_k == 3
        assert ws.search_params == {"language": "en"}

    def test_run_returns_documents_and_links(self, mock_client):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"), top_k=10)
        ws._scavio_client = mock_client

        result = ws.run(query="test query")

        assert len(result["documents"]) == 1
        assert isinstance(result["documents"][0], Document)
        assert result["documents"][0].content == "Example content"
        assert result["documents"][0].meta["url"] == "https://example.com"
        assert result["documents"][0].meta["title"] == "Example Title"
        assert result["links"] == ["https://example.com"]
        mock_client.google.search.assert_called_once_with("test query")

    def test_run_overrides_params_at_runtime(self, mock_client):
        ws = ScavioWebSearch(
            api_key=Secret.from_token("test-key"),
            top_k=10,
            search_params={"country_code": "gb"},
        )
        ws._scavio_client = mock_client

        ws.run(query="test", search_params={"country_code": "us"})

        mock_client.google.search.assert_called_once_with("test", gl="us")

    def test_run_maps_params_to_v2(self, mock_client):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"), top_k=10)
        ws._scavio_client = mock_client

        ws.run(
            query="test",
            search_params={
                "country_code": "gb",
                "language": "en",
                "page": 3,
                "device": "mobile",
                "nfpr": True,
                "search_type": "news",
                "light_request": False,
            },
        )

        mock_client.google.search.assert_called_once_with(
            "test", gl="gb", hl="en", start=20, device="mobile", nfpr=True
        )

    def test_run_page_one_omits_start(self, mock_client):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._scavio_client = mock_client
        ws.run(query="test", search_params={"page": 1})
        mock_client.google.search.assert_called_once_with("test")

    def test_run_respects_top_k(self, mock_client):
        mock_client.google.search.return_value = {
            "organic_results": [{"title": f"r{i}", "link": f"https://x/{i}", "snippet": "c"} for i in range(20)]
        }
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"), top_k=3)
        ws._scavio_client = mock_client
        result = ws.run(query="test")
        assert len(result["documents"]) == 3
        assert len(result["links"]) == 3

    @pytest.mark.asyncio
    async def test_run_async(self, mock_async_client):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"), top_k=10)
        ws._async_scavio_client = mock_async_client

        result = await ws.run_async(query="test query")

        assert len(result["documents"]) == 1
        assert result["links"] == ["https://example.com"]
        mock_async_client.google.search.assert_awaited_once()

    def test_run_raises_on_error(self, mock_client):
        mock_client.google.search.side_effect = Exception("API error")
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._scavio_client = mock_client

        with pytest.raises(Exception, match="API error"):
            ws.run(query="test")

    @pytest.mark.asyncio
    async def test_run_async_raises_on_error(self, mock_async_client):
        mock_async_client.google.search = AsyncMock(side_effect=Exception("API error"))
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._async_scavio_client = mock_async_client

        with pytest.raises(Exception, match="API error"):
            await ws.run_async(query="test")

    def test_warm_up_initializes_clients(self):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        assert ws._scavio_client is None
        assert ws._async_scavio_client is None
        ws.warm_up()
        assert ws._scavio_client is not None
        assert ws._async_scavio_client is not None

    def test_run_triggers_warm_up(self, search_response):
        with (
            patch("haystack_integrations.components.websearch.scavio.scavio_websearch.ScavioClient") as mock_cls,
            patch("haystack_integrations.components.websearch.scavio.scavio_websearch.AsyncScavioClient"),
        ):
            mock_cls.return_value.google.search.return_value = search_response
            ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
            ws.run(query="test")
            mock_cls.assert_called_once_with(api_key="test-key")

    @pytest.mark.asyncio
    async def test_run_async_triggers_warm_up(self, search_response):
        with (
            patch("haystack_integrations.components.websearch.scavio.scavio_websearch.ScavioClient"),
            patch("haystack_integrations.components.websearch.scavio.scavio_websearch.AsyncScavioClient") as mock_cls,
        ):
            mock_cls.return_value.google.search = AsyncMock(return_value=search_response)
            ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
            await ws.run_async(query="test")
            mock_cls.assert_called_once_with(api_key="test-key")

    def test_run_empty_results(self, mock_client):
        mock_client.google.search.return_value = {"organic_results": []}
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._scavio_client = mock_client
        result = ws.run(query="obscure query")
        assert result["documents"] == []
        assert result["links"] == []

    def test_run_raises_runtime_error_when_warm_up_fails_to_initialize_client(self, monkeypatch):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        monkeypatch.setattr(ws, "warm_up", lambda: None)
        with pytest.raises(RuntimeError, match="ScavioWebSearch client failed to initialize"):
            ws.run(query="test")

    @pytest.mark.asyncio
    async def test_run_async_raises_runtime_error_when_warm_up_fails_to_initialize_client(self, monkeypatch):
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        monkeypatch.setattr(ws, "warm_up", lambda: None)
        with pytest.raises(RuntimeError, match="ScavioWebSearch async client failed to initialize"):
            await ws.run_async(query="test")

    def test_surface_is_exactly_one_endpoint(self, search_response):
        """This package is curated: one component, one endpoint (POST /api/v2/google).

        A client that raises on every namespace except `google` proves nothing else is
        reachable, so the credit note in the README ("flat 1 credit") stays true.
        """

        class _StrictClient:
            def __init__(self, response):
                self.google = MagicMock()
                self.google.search.return_value = response

            def __getattr__(self, name):
                msg = f"curated surface: {name} is not exposed by scavio-haystack"
                raise AssertionError(msg)

        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._scavio_client = _StrictClient(search_response)
        assert ws.run(query="test")["links"] == ["https://example.com"]

    def test_module_exports_only_the_websearch_component(self):
        """Every public Scavio* name is declared in __all__; nothing undeclared leaks out."""
        import haystack_integrations.components.websearch.scavio as pkg

        exported = {n for n in dir(pkg) if n.startswith("Scavio")}
        assert "ScavioWebSearch" in exported
        assert exported == set(pkg.__all__)

    def test_v1_google_vocabulary_never_reaches_the_sdk(self, mock_client):
        """/api/v1/google is retired (410). v1-only keys must be dropped, not forwarded."""
        ws = ScavioWebSearch(api_key=Secret.from_token("test-key"))
        ws._scavio_client = mock_client
        ws.run(query="test", search_params={"light_request": True, "search_type": "news", "country_code": "us"})
        _, kwargs = mock_client.google.search.call_args
        assert "light_request" not in kwargs
        assert "search_type" not in kwargs
        assert kwargs == {"gl": "us"}

    @pytest.mark.skipif(
        not os.environ.get("SCAVIO_API_KEY"),
        reason="Export SCAVIO_API_KEY to run integration tests.",
    )
    @pytest.mark.integration
    def test_run_integration(self):
        ws = ScavioWebSearch(api_key=Secret.from_env_var("SCAVIO_API_KEY"), top_k=3)
        result = ws.run(query="What is Haystack by deepset?")
        assert len(result["documents"]) > 0
        assert len(result["links"]) > 0
        assert isinstance(result["documents"][0], Document)

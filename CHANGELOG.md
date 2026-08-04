# Changelog

## [v0.1.3]

### Changed

- Raise the `scavio` floor to `>=0.14.0`, the release that carries the full
  namespace set (X, LinkedIn, TikTok Shop and the 14 Google v2 verticals).
  Nothing in `ScavioWebSearch` needs them, but the floor keeps the installed
  SDK in step with the rest of the Scavio ecosystem.
- README: state the scope explicitly. This package exposes exactly **1** of
  Scavio's 98 endpoints (`POST /api/v2/google`, 1 credit) and stays that way
  by design; the hosted MCP server is the route to the rest of the API.

## [v0.1.2]

### Changed

- Raise the `scavio` floor to `>=0.13.0`. `ScavioWebSearch` calls
  `google.search` with the Google v2 vocabulary (`gl`, `hl`, `start`,
  `google_domain`), which older SDKs route to the retired `/api/v1/google`
  endpoint. `/api/v1/google` hard-sunsets on 2026-08-04.

## [v0.1.1]

### Changed

- `ScavioWebSearch` targets Google v2: `country_code` maps to `gl`, `language`
  to `hl`, and `page` to `start=(page-1)*10`. The v1-only `search_type` and
  `light_request` keys are dropped. Results are read from `organic_results`,
  using each item's `link` and `snippet`.

## [v0.1.0]

### Features

- Add `ScavioWebSearch` component: web search backed by the Scavio API, returning
  Haystack `Document`s and source links, with sync `run` and async `run_async`.

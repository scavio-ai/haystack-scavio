# Changelog

The version is derived from the git tag by `hatch-vcs`, and PyPI is published by
the tag push. A heading here is therefore only real if a matching `vX.Y.Z` tag
exists.

## [v0.1.4]

### Changed

- README: most Instagram calls cost 2 credits (was 2-10).

## [v0.1.3]

### Changed

- README: YouTube transcripts cost 5 credits (was 8).

## [v0.1.2]

> **Ledger correction.** Earlier revisions of this file carried `[v0.1.2]` and
> `[v0.1.3]` headings. Neither version was ever tagged and neither reached PyPI,
> which is still on `0.1.1` — the code they described has sat on `main`,
> unreleased, since it was written. The two headings are collapsed into this one
> entry, which ships as `v0.1.2` when the tag is cut. Nothing was published under
> `0.1.3` at the time; the later v0.1.3 above is an unrelated README release.

### Changed

- Raise the `scavio` floor to `>=0.15.0`. `ScavioWebSearch` needs nothing beyond
  `google.search`, but a lower floor lets a resolver install an SDK without the
  namespaces every other Scavio package now assumes, so the floor moves with the
  ecosystem. This also supersedes the never-released `>=0.13.0` and `>=0.14.0`
  bumps.
- README: correct the counts. Scavio is at 195 endpoints — 194 across 31
  platforms, plus `extract` — where the README said "98 endpoints across ten
  platforms", and the hosted MCP server exposes 191 tools where it said 100.
  The most recent batch added 93 endpoints across 22 platforms plus `extract`,
  21 of those platforms new; **none of them are reachable through this
  package**, whose surface is unchanged at 1 component and 1 endpoint.
- README: name the body-priced surfaces (Walmart, Threads, Kuaishou, `extract`)
  in the credits note rather than implying every endpoint has a flat price, and
  document `extract` as the top-level `client.extract(url)` — it is not a
  namespace.
- Test suite: pin the `scavio` floor with a test, so the manifest and the
  ecosystem cannot silently drift apart again.

### Fixed

- Lint: ignore `PLC0415` under `tests/`. Ruff promoted the rule to stable after
  this repo was written, which made `hatch run fmt-check` fail on an
  export-inspection test that imports the package inside the test body on
  purpose. The failure predates this release and had nothing to do with the
  package surface.

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

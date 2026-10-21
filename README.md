# TileOPs Documentation

The documentation site for [TileOPs](https://github.com/yyttt6/TileOPs) — spec-driven
LLM operators across backends, built on TileLang.

**Live site**: [yyttt6.github.io/TileOPs.github.io](https://yyttt6.github.io/TileOPs.github.io/)

MkDocs + Material. GitHub Actions deploys to `gh-pages` on every push to `main`,
and uses the dedicated remote nightly for official Ascend 950 performance results.

## Local development

```bash
pip install mkdocs-material "mkdocstrings[python]" mkdocs-include-markdown-plugin \
  mkdocs-static-i18n jieba pyyaml black

# The API and design pages read from a TileOPs checkout at ./TileOPs. The
# workflows clone it there; locally, clone it too — or point a symlink at a
# clone you already have. Either way the path is gitignored.
git clone --depth 1 https://github.com/yyttt6/TileOPs.git TileOPs

mkdocs serve
```

Two things to know before the first run.

- **The URL carries a subpath.** `site_url` ends in `/TileOPs.github.io/`, so
  that, not `/`, is the page `mkdocs serve` prints.
- **The checkout is not optional.** Without it, mkdocstrings cannot import
  `tileops`, and the build aborts rather than warns.

To see real numbers on the Benchmarks pages, run `bash scripts/render_bench.sh`:
it renders eligible official data, or an empty section until such data exists. They are generated output —
change the renderer, never the pages.

## Layout

Pages live under `docs/`. `mkdocs.yml` holds the nav, theme and plugins, and its
nav is the current page list.

Three groups of pages are not written by hand:

- `docs/api/` — generated from TileOPs docstrings by mkdocstrings.
- `docs/design/` — mirrored from that repo's `docs/design/` at build time.
- `docs/benchmarks/` — rendered from an eligible official Ascend 950 snapshot at deploy time.

`hooks.py` cleans up after the first two and stands in for the third: it rewrites
the repo-relative paths mirrored content arrives with, and expands the single
Benchmarks nav entry, since those pages do not exist until the renderer has run.

## Bilingual pages

English lives at the site root, Chinese under `/zh/`.

A Chinese page is a `<name>.zh.md` beside the English `<name>.md`, written as
prose rather than as an include shell. Some pages are drafted in Chinese and
translated into English, so a page's two versions are kept in step by hand.

A page with no translation falls back to English at the same URL, with a notice
prepended by `hooks.py` — so the Chinese nav is never sparse.

## Official Ascend 950 publication

Benchmark pages use the upstream renderer and family layout, pinned at
`tile-ai/TileOPs.github.io@9c575b45a428ee8c4fce706b83fc85af3231d3a9`.
The small platform adaptation replaces the measurement-method text when the
snapshot explicitly declares `ascend950-profiler-locked-v1`.

Only the dedicated remote nightly can publish performance comparisons. No valid
snapshot is available yet, so the section is empty. Local correctness CI and
historical unlocked timings are never consumed by the site renderer.

Run `bash scripts/render_bench.sh` to build the empty section. A validated official
snapshot may be supplied through `ASCEND950_OFFICIAL_SNAPSHOT`. It must identify
the remote publisher, locked protocol, successful guard and matched comparisons.
The remote nightly is being provisioned for **00:00 UTC** against the latest
`ascend950` commit. Device execution and publication remain blocked until host
clock control, restore and shared device reservation are available.

910B1 data remains in `data/archive/ascend910b1-20261021/` and the original source
branch `archive/ascend910b1-20261021`. The withdrawn custom 950 pages and evidence
remain in `data/archive/website-before-formal-ci-20261021/` and Git history. None
of these archives is copied into the public performance pages.

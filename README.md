# TileOPs Documentation

The documentation site for [TileOPs](https://github.com/yyttt6/TileOPs) — spec-driven
LLM operators across backends, built on TileLang.

**Live site**: [yyttt6.github.io/TileOPs.github.io](https://yyttt6.github.io/TileOPs.github.io/)

MkDocs + Material. GitHub Actions deploys to `gh-pages` on every push to `main`,
and refreshes the Ascend 950 CI results hourly.

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
it validates the committed Ascend 950 evidence and renders it. They are generated output —
change the renderer, never the pages.

## Layout

Pages live under `docs/`. `mkdocs.yml` holds the nav, theme and plugins, and its
nav is the current page list.

Three groups of pages are not written by hand:

- `docs/api/` — generated from TileOPs docstrings by mkdocstrings.
- `docs/design/` — mirrored from that repo's `docs/design/` at build time.
- `docs/benchmarks/` — rendered from validated Ascend 950 JSON at deploy time.

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

## Ascend 950 data publication

- `data/ascend950/current-ci.json`: latest successful `ascend950` correctness CI.
- `data/ascend950/development-v2.json`: reviewed October 18–20 development measurements,
  with all 15 samples per side and source hashes. These predate TileLang 0.1.15,
  were not clock locked, and are never presented as release performance results.
- `data/archive/ascend910b1-20261021/`: complete original 910B1 nightly snapshot,
  pinned commit and SHA-256 manifest. Original site source is preserved on
  `archive/ascend910b1-20261021`; historical supplementary pages live in
  `docs/archive/ascend910b1/`.

Deploy and hourly refresh use the workflow's `GITHUB_TOKEN` to fetch the public
`yyttt6/TileOPs` repository's latest successful trusted Ascend 950 CI artifact.
Failed or expired evidence aborts publication. The last deployed site stays intact.
No device benchmark runs in the documentation workflow.

```bash
# Reproduce the reviewed performance import from the development workspace:
python scripts/import_ascend950.py --workspace /path/to/workspace
# Explicit live CI refresh (GH_TOKEN or GITHUB_TOKEN required for artifact download):
ASCEND950_SYNC_CI=1 bash scripts/render_bench.sh
# Offline rendering from the committed snapshot:
bash scripts/render_bench.sh
```

The existing API/design pages retain the separately pinned legacy documentation
checkout. Ascend 950's current implementation and benchmark guide are linked to
`yyttt6/TileOPs:ascend950` from the result pages.

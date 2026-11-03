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

### Baseline cache progress

The benchmark family pages currently display the explicit, frozen baseline cache
snapshot in `data/baseline-cache/snapshot.json`. This progress publication was
authorized on 2026-10-29 and includes measured results from all three machines.
It uses platform default clocks, full correctness receipts and exclusive guard
receipts, with 3 warmups, 15 samples and 1 GiB cache eviction. Stored profiler kernel-duration sums are preferred (including overlapping kernels);
wall-clock measurements are used when device samples are unavailable. Timing
provenance stays in the internal publication audit. Machine labels are omitted from the
public pages and download; detailed provenance remains in the internal receipts.
Missing TileOPs timings stay null
and ratios render as NaN. Cache coverage does not establish complete baseline
coverage or acceptance of a TileOPs implementation.

`scripts/render_baseline_cache.py` generates these pages after the official
renderer. The raw sanitized snapshot is downloadable from the benchmark index.
The historical official-nightly instructions below describe the separate paired
comparison pipeline; its old clock-lock requirement was revoked by the user on
2026-10-22 and is not applied to this cache publication.

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
The `Official Ascend 950 nightly` workflow is scheduled for **00:00 UTC**. GitHub
may delay scheduled jobs when its queues are busy. It resolves the latest
`ascend950` commit once, runs CPU contracts, then runs the exact same commit on
the dedicated `ascend950-production` ARM64 runner. Publication requires that job
to succeed. Site-only deployments reuse the latest successful remote artifact;
they never fetch results from the local correctness runner.

Persistent configuration and source backups live at
`/workspace/user_data/tileops-ci`. Deploy `ci/ascend950-env.sh` as `env.sh` and the
site configuration as `site.json` there. Install Python, the runtime, `bin/uv`,
the runner and its working directory under `/opt/tileops-ci` on the container's
local filesystem. The platform's shared FUSE volume reproduced duplicate bytes
on append writes with both Python and Node; it must not hold active runner files,
virtual environments or compiler caches. Keep the runtime's package freeze at
`/workspace/user_data/tileops-ci/runtime-freeze.txt`.
The example intentionally leaves `host_reservation_confirmed` false: an
administrator must provide host-shared reservation/PID visibility and a verified
clock lock/restore tool before device execution. Merely having `npu-smi` inside
a container does not establish either capability. Do not turn this flag on to
bypass an unavailable host interface.

The runner listener starts with `ci/start-ascend950-runner.sh`. In a container
without systemd, the platform's startup hook must invoke it again after container
restart. Recreate local installations if the platform replaces the container's
local filesystem. It performs no device work; each benchmark command acquires the separate
host NPU reservation. Raw evidence is retained in Actions artifacts, outside the
public performance pages. An empty baseline factory list produces no performance
rows; baseline source identity and matched measurements are required to populate
the tables.

910B1 data remains in `data/archive/ascend910b1-20261021/` and the original source
branch `archive/ascend910b1-20261021`. The withdrawn custom 950 pages and evidence
remain in `data/archive/website-before-formal-ci-20261021/` and Git history. None
of these archives is copied into the public performance pages.

### Ascend 950 nightly on server2

The website nightly starts from the daily `19:00 UTC` schedule (03:00 Asia/Shanghai;
GitHub may delay scheduled jobs). It freezes `ascend950` at the contracts job,
uses the canonical release SDK/runtime profile on physical 32 Cube / 64 Vector
hardware, and takes one shared `npu-guard` reservation per registered operator.
The website runner requires both `ascend950-production` and `ascend950-server2`.

New TileOPs samples use platform-default clocks, three warmups, fifteen isolated
NPU profiler windows, and 1 GiB cache eviction. Distinct task spans count mixed
AIC/AIV roles once; named AICPU work is included. Saved traces are hashed and
replayed before publication. Historical native baselines retain their admitted
original v2 values; nightly does not remeasure them or relabel them as v3.
Only exact workload contracts are joined. Previous unrelated results retain their
measurement identities; new results identify the measured commit and date.

A successful workflow means complete correctness and valid measurements for the
selected registered operators, not that every performance ratio reaches 0.8.
Guard infrastructure exits 75, 76 and 78 allow one full retry under a new reservation,
with both attempts retained; numerical failures are never retried automatically.
Any failed operator or invalid final guard receipt blocks this publication and preserves
the last successful snapshot. Raw evidence, per-operator elapsed time (including
reservation wait), compact publication evidence, and the source revision are
uploaded by the workflow. The final Actions duration additionally includes CPU
contracts, environment preparation, artifact upload and site deployment.

The container runner supervisor lives at
`/opt/tileops-ci/nightly-server2-20261103/start-runner.sh`; it uses a process lock
and may be restarted without starting a second listener. Device jobs always run
in the foreground under the shared NPU reservation.

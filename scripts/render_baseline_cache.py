"""Render an explicitly published cache snapshot in the existing family layout."""
import html
import json
import math
import re
import shutil
from collections import defaultdict
from pathlib import Path

from gen_bench_pages import (
    _MANIFEST_FAMILY,
    DATA_PAGES,
    DETAIL_FOOTER,
    DETAIL_HEADER,
    _label_html,
    _sig_ms,
    _stack,
)
from workload_shape import DTYPE_ABBR

ROOT = Path(__file__).resolve().parents[1]


def cell(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ')


def label_dtype(case):
    parts, dtypes = case.split('-'), []
    while len(parts) > 1 and parts[-1] in DTYPE_ABBR:
        dtypes.insert(0, DTYPE_ABBR[parts.pop()])
    return '-'.join(parts), '/'.join(dtypes) or '·'


def render():
    source = ROOT / 'data/baseline-cache/snapshot.json'
    if not source.exists():
        return
    data = json.loads(source.read_text())
    rows = list(data['rows'])
    baseline_count = len(rows)
    baseline_cases = {(r['op'], r['case']) for r in rows}
    identities = set()
    for row in rows:
        assert not {'host', 'cohort', 'metric', 'original_metric'} & row.keys(), 'Measurement provenance must remain private'
        key = (row['library'], row['op'], row['case'])
        assert key not in identities, 'Duplicate measurement'
        identities.add(key)
        assert row['samples'] == 15 and math.isfinite(row['latency_us']) and row['latency_us'] > 0
        tile = row['tileops_latency_us']
        if tile is None:
            assert row['ratio'] is None
        else:
            assert math.isfinite(tile) and tile > 0
            assert row.get('tileops_samples') == 15
            assert row.get('tileops_verified') is True
            assert math.isfinite(row['ratio']) and math.isclose(row['ratio'], row['latency_us'] / tile, rel_tol=1e-9)
    timings = defaultdict(set)
    for row in rows:
        timings[(row['op'], row['case'])].add(row['tileops_latency_us'])
    assert all(len(values) == 1 for values in timings.values()), 'Inconsistent TileOPs timing for the same workload'
    for tile in data.get('tileops_rows', []):
        assert not {'host', 'cohort', 'metric', 'original_metric'} & tile.keys(), 'Measurement provenance must remain private'
        key = (tile['op'], tile['case'])
        assert key not in timings, 'Duplicate or overlapping TileOPs-only measurement'
        assert tile['samples'] == 15 and tile['verified'] is True
        assert math.isfinite(tile['latency_us']) and tile['latency_us'] > 0
        timings[key].add(tile['latency_us'])
        rows.append(dict(library=None, op=tile['op'], case=tile['case'],
                         workload=tile['workload'], latency_us=None, samples=None,
                         tileops_latency_us=tile['latency_us'], ratio=None))
    out = ROOT / 'docs/benchmarks'
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out / 'baseline-cache.json')
    # This view reports cached baselines. The official matched-comparison renderer
    # retains its own admission rules; no synthetic TileOPs measurements are made.
    for path in out.glob('*.md'):
        path.unlink()
    cases = {(r['op'], r['case']) for r in rows}
    tileops_cases = {(r['op'], r['case']) for r in rows if r['tileops_latency_us'] is not None}
    tileops_ops = {op for op, _ in tileops_cases}
    ops = {r['op'] for r in rows}
    intro = ('Baseline cache progress · Ascend 950DT · snapshot ' + data['frozen_at'] + '\n\n'
             'Latencies are measured results on Ascend 950DT with 32 AI Cores. '
             'Ratio is the fastest listed baseline time divided by TileOPs time. '
             'A verified matching TileOPs result is required; otherwise **Ratio = NaN** '
             'and TileOPs latency is **—**. A verified TileOPs timing without an eligible '
             'baseline is shown with **Ratio = NaN**.\n\n'
             'Times are in milliseconds. '
             'Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. '
             'Only cache records with complete successful correctness and guard receipts are included. '
             'The most recent eligible measurement per baseline / case is shown.\n\n'
             '[Download measurements](baseline-cache.json).\n\n')
    index = ['# Benchmarks\n\n', intro,
             f"**{len(ops)} operators · {len(baseline_cases)} / {data['manifest_cases']} workloads with a baseline · "
             f"{baseline_count} baseline measurements.**\n\n",
             f"**Verified TileOPs results: {len(tileops_ops)} operators · {len(tileops_cases)} workloads.**\n\n",
             'Coverage is partial: a measured workload can still have other baselines pending. '
             'These are recorded results, not a claim that an operator is fully covered.\n\n',
             '## Baseline coverage\n\n| Baseline | Measurements |\n| --- | ---: |\n']
    for lib in sorted({r['library'] for r in rows if r['library'] is not None}):
        count = sum(r['library'] == lib for r in rows)
        index.append('| ' + cell(lib) + ' | ' + str(count) + ' |\n')
    index.append('\n## Data\n\n| Page | Operators | Workloads | Baseline measurements |\n| --- | ---: | ---: | ---: |\n')
    (out / 'method.md').write_text('# How these numbers are taken\n\n' + intro +
        'The shared measurement workflow supplies baseline latencies. The downloadable '
        'snapshot retains a measurement identifier for every result.\n\n'
        'Ratio, TileOPs device time, throughput, SOL and bound remain unavailable when '
        'the corresponding TileOPs measurement or roofline calibration is absent.\n')
    order = {}
    for api in sorted((ROOT / 'docs/api').glob('*.md')):
        for name in re.findall(r'^::: tileops\.(?:\w+\.)+(\w+)\s*$', api.read_text(), re.MULTILINE):
            order.setdefault(name.removesuffix('Op'), len(order))
    def page_family(row):
        family = row['workload'].get('family', 'other')
        return _MANIFEST_FAMILY.get(family, family)

    assigned = set()
    for slug, title, families in DATA_PAGES:
        selected = [r for r in rows if page_family(r) in families]
        if slug == 'other':
            selected += [r for r in rows if page_family(r) not in
                         {f for _, _, fs in DATA_PAGES for f in fs}]
        if not selected:
            continue
        text = [f'# {title}\n\n',
                f"{len({r['op'] for r in selected})} ops, "
                f"{len({(r['op'], r['case']) for r in selected})} workloads.\n\n",
                'One table per op, one row per workload and dtype. '
                'Times are in ms. Ratio compares the fastest listed baseline with the verified TileOPs result; missing results show NaN. '
                '[How these numbers are taken](method.md).\n\n']
        grouped = defaultdict(list)
        for row in selected:
            grouped[row['op']].append(row)
            assigned.add((row['library'], row['op'], row['case']))
        for op, values in sorted(grouped.items(), key=lambda x: (order.get(x[0].removesuffix('Op'), 10000), x[0])):
            text.append(f'## {cell(op.removesuffix("Op"))}\n\n')
            specs = {}
            for row in values:
                label, dtype = label_dtype(row['case'])
                shapes = '; '.join(f'{name}: {tensor[0]}' for name, tensor in
                                   row['workload'].get('tensors', {}).items())
                specs.setdefault(label, (shapes, set()))[1].add(dtype)
            text.append('<div class="wl-key"><ul class="wl-rows">\n')
            for label, (shapes, dtypes) in sorted(specs.items()):
                text.append(f'<li><code class="wl-id">{_label_html(label)}</code>'
                            f'<span class="wl-delta">{cell(shapes)} · dtype={cell(", ".join(sorted(dtypes)))}</span></li>\n')
            text.append('</ul></div>\n\n')
            workloads = defaultdict(list)
            for row in values:
                workloads[row['case']].append(row)
            text.append('\n'.join(DETAIL_HEADER) + '\n')
            groups = defaultdict(list)
            for case, measures in workloads.items():
                label, dtype = label_dtype(case)
                groups[label].append((dtype, measures))
            for label, dtype_rows in sorted(groups.items()):
                for number, (dtype, measures) in enumerate(sorted(dtype_rows)):
                    measures.sort(key=lambda r: (r['latency_us'] if r['latency_us'] is not None else math.inf, r['library'] or ''))
                    names = _stack([f"<code>{cell(r['library'])}</code>" if r['library'] is not None else '—' for r in measures])
                    times = _stack([_sig_ms(r['latency_us'] / 1000) if r['latency_us'] is not None else '—' for r in measures])
                    name = (f'<td class="wl-name" rowspan="{len(dtype_rows)}">'
                            f'<code>{_label_html(label)}</code></td>') if number == 0 else ''
                    tile = measures[0]['tileops_latency_us']
                    ratio_text = 'NaN' if tile is None or measures[0]['latency_us'] is None else f"{measures[0]['latency_us'] / tile:.2f}"
                    tile_text = '—' if tile is None else _sig_ms(tile / 1000)
                    text.append(f'<tr>{name}<td class="colsep">{cell(dtype)}</td>'
                                f'<td>{ratio_text}</td><td>{tile_text}</td><td>{names}</td><td>{times}</td>'
                                '<td>·</td><td>·</td><td>·</td></tr>\n')
            text.append('\n'.join(DETAIL_FOOTER) + '\n\n')
        (out / (slug + '.md')).write_text(''.join(text))
        index.append(f'| [{title}]({slug}.md) | {len(grouped)} | '
                     f"{len({(r['op'], r['case']) for r in selected})} | {sum(r['library'] is not None for r in selected)} |\n")
    assert len(assigned) == len(rows), 'Every published measurement must appear in a family table'
    (out / 'index.md').write_text(''.join(index))
    print(f'Baseline snapshot: {len(rows)} measurements, {len(cases)} workloads, {len(ops)} operators')


if __name__ == '__main__':
    render()

"""Render an explicitly published cache snapshot in the existing family layout."""
import html
import json
import math
import shutil
from collections import defaultdict
from pathlib import Path

from gen_bench_pages import DATA_PAGES

ROOT = Path(__file__).resolve().parents[1]


def cell(value):
    return html.escape(str(value)).replace('|', '&#124;').replace('\n', ' ')


def render():
    source = ROOT / 'data/baseline-cache/snapshot.json'
    if not source.exists():
        return
    data = json.loads(source.read_text())
    rows = data['rows']
    identities = set()
    for row in rows:
        key = (row['host'], row['library'], row['op'], row['case'])
        assert key not in identities, 'Duplicate measurement'
        identities.add(key)
        assert row['samples'] == 15 and math.isfinite(row['latency_us']) and row['latency_us'] > 0
        assert row['ratio'] is None and row['tileops_latency_us'] is None
        assert row['metric'] in ('device_latency_ms', 'end_to_end_mean_ms')
    out = ROOT / 'docs/benchmarks'
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, out / 'baseline-cache.json')
    # This view reports cached baselines. The official matched-comparison renderer
    # retains its own admission rules; no synthetic TileOPs measurements are made.
    for path in out.glob('*.md'):
        path.unlink()
    cases = {(r['op'], r['case']) for r in rows}
    ops = {r['op'] for r in rows}
    intro = ('Baseline cache progress · Ascend 950DT · snapshot ' + data['frozen_at'] + '\n\n'
             'Latencies are measured baseline results. TileOPs timings are not included in this '
             'cache snapshot, so **Ratio = NaN** and TileOPs latency is **—**. '
             'This does not rate unfinished operators or claim performance acceptance.\n\n'
             'Machines are displayed separately; results from different hosts or software cohorts '
             'are not used to calculate a speedup. Each baseline cell shows microseconds; '
             '`D` = profiler device latency, `H` = complete host round-trip latency. '
             'Platform default clocks; 3 warmups, 15 samples and 1 GiB cache eviction. '
             'Only cache records with complete successful correctness and guard receipts are included. '
             'The most recent valid record per host / baseline / case is shown.\n\n'
             '[Download measurements and provenance](baseline-cache.json).\n\n')
    index = ['# Benchmarks\n\n', intro,
             f"**{len(ops)} operators · {len(cases)} / {data['manifest_cases']} workloads with a baseline · "
             f"{len(rows)} baseline measurements across 3 machines.**\n\n",
             'Coverage is partial: a measured workload can still have other baselines pending. '
             'These are recorded results, not a claim that an operator is fully covered.\n\n',
             '## Baseline coverage\n\n| Baseline | Local | Server 1 | Server 2 | Total |\n| --- | ---: | ---: | ---: | ---: |\n']
    for lib in sorted({r['library'] for r in rows}):
        counts = [sum(r['library'] == lib and r['host'] == host for r in rows)
                  for host in ('local', 'server1', 'server2')]
        index.append('| ' + cell(lib) + ' | ' + ' | '.join(map(str, counts + [sum(counts)])) + ' |\n')
    index.append('\n## Data\n\n| Page | Operators | Workloads | Baseline measurements |\n| --- | ---: | ---: | ---: |\n')
    assigned = set()
    for slug, title, families in DATA_PAGES:
        selected = [r for r in rows if r['workload'].get('family', 'other') in families]
        if slug == 'other':
            selected += [r for r in rows if r['workload'].get('family', 'other') not in
                         {f for _, _, fs in DATA_PAGES for f in fs}]
        if not selected:
            continue
        text = [f'# {title}\n\n', intro]
        grouped = defaultdict(list)
        for row in selected:
            grouped[row['op']].append(row)
            assigned.add((row['host'], row['library'], row['op'], row['case']))
        for op, values in sorted(grouped.items()):
            text.append(f'## {cell(op)}\n\n')
            libs = sorted({r['library'] for r in values})
            text.append('| Workload | Machine | Ratio | TileOPs (µs) | ' + ' | '.join(cell(x) + ' (µs)' for x in libs) + ' |\n')
            text.append('| --- | --- | ---: | ---: | ' + ' | '.join('---:' for _ in libs) + ' |\n')
            workloads = defaultdict(dict)
            for row in values:
                workloads[(row['case'], row['host'])][row['library']] = row
            for (case, host), measures in sorted(workloads.items()):
                cells = []
                for lib in libs:
                    r = measures.get(lib)
                    cells.append('—' if r is None else f"{r['latency_us']:.3f} {'D' if r['metric'] == 'device_latency_ms' else 'H'}")
                text.append('| ' + cell(case) + ' | ' + host + ' | NaN | — | ' + ' | '.join(cells) + ' |\n')
            text.append('\n')
        (out / (slug + '.md')).write_text(''.join(text))
        index.append(f'| [{title}]({slug}.md) | {len(grouped)} | '
                     f"{len({(r['op'], r['case']) for r in selected})} | {len(selected)} |\n")
    assert len(assigned) == len(rows), 'Every published measurement must appear in a family table'
    (out / 'index.md').write_text(''.join(index))
    print(f'Baseline snapshot: {len(rows)} measurements, {len(cases)} workloads, {len(ops)} operators')


if __name__ == '__main__':
    render()

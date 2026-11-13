"""Keep published baselines authoritative while joining only matching TileOPs contracts."""
import copy
import json
import math


def contract(row):
    def normalize(value):
        if isinstance(value, float) and not math.isfinite(value):
            return 'NaN' if math.isnan(value) else ('Infinity' if value > 0 else '-Infinity')
        if isinstance(value, dict):
            return {k: normalize(v) for k, v in value.items()}
        if isinstance(value, list):
            return [normalize(v) for v in value]
        return value
    return json.dumps(normalize(row['workload']['params']), sort_keys=True)


def identity(row):
    from baseline_contracts import comparison_identity
    return comparison_identity(row['op'], row['case'], row['workload']['params'])


def merge_latest_release(official, published, release):
    """An older nightly may add TileOPs evidence, never roll back a baseline release."""
    data = copy.deepcopy(published)
    actual = {(r['library'], r['op'], r['case']): r for r in data['rows']}
    assert len(actual) == release['count'] == len(release['measurements'])
    for item in release['measurements']:
        row = actual[(item['library'], item['op'], item['case'])]
        assert all(row[k] == item[k] for k in ('measurement_id', 'protocol'))
    tiles = {}

    def offer(row, candidate):
        key = identity(row)
        previous = tiles.get(key)
        if previous is None or candidate.get('tileops_date', '') > previous.get('tileops_date', ''):
            tiles[key] = candidate
        elif candidate.get('tileops_date', '') == previous.get('tileops_date', ''):
            assert candidate['tileops_latency_us'] == previous['tileops_latency_us'], (
                'Conflicting TileOPs timings for the same contract and date'
            )

    for row in official['rows'] + official.get('historical_rows', []):
        if row.get('tileops_latency_us') is not None:
            offer(row, {k: v for k, v in row.items() if k.startswith('tileops_')})
    for tile in official.get('tileops_rows', []) + official.get('historical_tileops_rows', []):
        offer(tile, {'tileops_' + k: v for k, v in tile.items()
                     if k in ('latency_us', 'samples', 'verified', 'protocol',
                              'measurement_id', 'commit', 'date')})
    for row in data['rows'] + data.get('historical_rows', []):
        candidate = tiles.get(identity(row))
        if candidate and (not row.get('tileops_date') or
                          candidate.get('tileops_date', '') >= row['tileops_date']):
            row.update(candidate)
            row['ratio'] = row['latency_us'] / row['tileops_latency_us']
    visible = {(r['op'], r['case']) for r in data['rows']}
    extra = {(r['op'], r['case']): r for r in data.get('tileops_rows', [])}
    for row in official.get('tileops_rows', []):
        if (row['op'], row['case']) not in visible:
            extra[(row['op'], row['case'])] = row
    visible_contracts = {identity(row) for row in data['rows']}
    # A renamed public op must not survive as a second baseline-less row after
    # its measurement has been joined to the equivalent published contract.
    data['tileops_rows'] = [row for row in extra.values()
                           if identity(row) not in visible_contracts]
    data['historical_tileops_rows'] = official.get('historical_tileops_rows', [])
    if 'nightly' in official:
        data['nightly'] = official['nightly']
    data['frozen_at'] = max(official['frozen_at'], published['frozen_at'])
    return data

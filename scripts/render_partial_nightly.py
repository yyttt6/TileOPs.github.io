"""Show an explicitly published partial run without presenting it as a passing nightly."""
import re
from datetime import datetime, timedelta, timezone

from baseline_contracts import comparison_identity


def render_progress(data, out):
    report = data.get('partial_nightly')
    if report is None:
        return
    assert report['status'] == 'partial' and report['termination'] == 'workflow_timeout'
    run = report['run_id']
    assert re.fullmatch(r'[0-9]+', run)
    operators = report['operators']
    by_op = {row['op']: row for row in operators}
    assert len(by_op) == len(operators) == report['total_operators']
    for key, status in [('passed_operators', 'passed'), ('failed_operators', 'failed'),
                        ('remaining_operators', 'not_completed')]:
        assert report[key] == sum(row['status'] == status for row in operators)
    assert report['completed_operators'] == report['passed_operators'] + report['failed_operators']
    assert report['fresh_cases'] == sum(row['cases'] for row in operators if row['status'] == 'passed')
    link = f'https://github.com/yyttt6/TileOPs.github.io/actions/runs/{run}'
    day = datetime.fromisoformat(report['started_at']).astimezone(timezone(timedelta(hours=8))).date()
    summary = (f"**Partial nightly · {day} (Asia/Shanghai) · "
               f"{report['completed_operators']}/{report['total_operators']} operators processed:** "
               f"{report['passed_operators']} passed, {report['failed_operators']} failed, "
               f"{report['remaining_operators']} not completed. The run reached its time limit. "
               f"{report['fresh_cases']} verified workloads from passing operators were refreshed. "
               'Failed and unfinished operators retain historical results, where available; '
               'those results do not establish a pass in this run. '
               '[Operator status](partial-nightly.md).\n\n')
    full = data.get('full_nightly')
    superseded = bool(full and datetime.fromisoformat(full['date']) >
                      datetime.fromisoformat(report['started_at']))
    index = out / 'index.md'
    text = index.read_text()
    if superseded:
        current = (f"**Latest full nightly: {full['registered_operators']} operators · "
                   f"{full['fresh_cases']} verified workloads · passed.** "
                   f"[Run](https://github.com/yyttt6/TileOPs.github.io/actions/runs/{full['run_id']}). "
                   "The older partial run is retained as [historical evidence](partial-nightly.md).\n\n")
    else:
        current = summary
    index.write_text(text.replace('# Benchmarks\n\n', '# Benchmarks\n\n' + current, 1))
    labels = {'passed': 'Passed', 'failed': 'Failed', 'not_completed': 'Not completed'}
    page = ['# Partial nightly results\n\n', summary,
            f'[Original nightly run]({link}) · source `{report["commit"]}`.\n\n',
            'Only complete passing operators with verified source hashes, correctness, guard receipts '
            'and replayed raw measurement windows contribute new timings. This is a partial publication, '
            'not a successful full nightly or a performance-acceptance claim.\n\n',
            '| Operator | This run | Planned cases | Refreshed cases |\n',
            '| --- | --- | ---: | ---: |\n']
    for row in operators:
        assert re.fullmatch(r'[A-Za-z0-9_]+', row['op'])
        fresh = row['cases'] if row['status'] == 'passed' else 0
        page.append(f"| {row['op']} | {labels[row['status']]} | {row['cases']} | {fresh} |\n")
    (out / 'partial-nightly.md').write_text(''.join(page))
    if superseded:
        return  # Old failures must never annotate the latest successful full run.
    for path in out.glob('*.md'):
        if path.name in ('index.md', 'partial-nightly.md', 'method.md'):
            continue
        def annotate(match):
            op = comparison_identity(match[1] + 'Op', '', {})[0]
            row = by_op.get(op)
            if row is None:
                return match[0]
            if row['status'] == 'passed':
                note = ('Passed in the partial nightly; new timings apply only to matching workload '
                        'contracts. Other displayed results retain their recorded history.')
            else:
                note = (f"{labels[row['status']]} in the partial nightly. Displayed timings, if any, "
                        'are historical; no new timings from this operator were published.')
            return match[0] + f'{note} [Run status](partial-nightly.md).\n\n'
        path.write_text(re.sub(r'^## ([A-Za-z0-9_]+)\n\n', annotate, path.read_text(), flags=re.MULTILINE))

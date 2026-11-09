"""Dispatch once at 02:00 Shanghai; never catch up missed nights during the day."""
import argparse
import datetime as dt
import fcntl
import json
import os
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

API = 'https://api.github.com/repos/yyttt6/TileOPs.github.io'
WORKFLOW = 'ascend950-nightly.yml'


def eligible(now):
    local = now.astimezone(ZoneInfo('Asia/Shanghai'))
    return local.hour == 2 and local.minute < 15


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    now = dt.datetime.now(dt.timezone.utc)
    if args.dry_run:
        print(json.dumps({'eligible_now': eligible(now), 'schedule': '02:00 Asia/Shanghai',
                          'dispatch': False}))
        return
    if not eligible(now):
        print('Outside 02:00-02:15 Shanghai; no late catch-up')
        return
    state = Path(os.environ.get('STATE_DIRECTORY', '/var/lib/tileops-nightly-dispatch'))
    state.mkdir(parents=True, exist_ok=True)
    with (state / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        marker = state / (now.astimezone(ZoneInfo('Asia/Shanghai')).date().isoformat() + '.json')
        if marker.exists():
            print('Already dispatched or outcome uncertain; no duplicate')
            return
        token = (Path(os.environ['CREDENTIALS_DIRECTORY']) / 'github_token').read_text().strip()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler(
            {'https': 'http://127.0.0.1:15014'}))

        def api(path, data=None):
            req = urllib.request.Request(API + path,
                data=json.dumps(data).encode() if data is not None else None,
                headers={'Authorization': 'Bearer ' + token,
                         'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
            with opener.open(req, timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else None

        if api(f'/actions/workflows/{WORKFLOW}')['state'] != 'active':
            print('Workflow disabled; respect pause')
            return
        runs = api(f'/actions/workflows/{WORKFLOW}/runs?per_page=30')['workflow_runs']
        if any(r['status'] != 'completed' for r in runs):
            print('Existing nightly active; skip this night without queueing a late run')
            return
        # Persist before POST: an ambiguous network failure must not create duplicates.
        record = {'at': now.isoformat(), 'status': 'sending'}
        marker.write_text(json.dumps(record))
        api(f'/actions/workflows/{WORKFLOW}/dispatches', {'ref': 'main'})
        record['status'] = 'dispatched'
        marker.write_text(json.dumps(record))
        print('Nightly dispatched for 02:00 Shanghai')


if __name__ == '__main__':
    main()

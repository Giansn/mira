#!/usr/bin/env python3
import json
import subprocess
import time
import os

SIM_PATH = '/home/ubuntu/.openclaw/workspace/scripts/telclaw-sim/simulator.py'
OUTPUT_DIR = '/home/ubuntu/.openclaw/workspace/simulation/telclaw_env'
SUMMARY_PATH = os.path.join(OUTPUT_DIR, 'dry_run_agent_summary.json')

SEEDS = [123, 999, 555, 777]


def run_once(seed, n=15):
    cmd = ['python3', SIM_PATH, '--seed', str(seed), '--n', str(n)]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        out = res.stdout
        # Try to parse JSON, else capture as text
        try:
            data = json.loads(out)
        except Exception:
            data = {'error': out}
        return {'seed': seed, 'data': data, 'exit_code': res.returncode}
    except Exception as e:
        return {'seed': seed, 'error': str(e)}


def main():
    results = []
    for s in SEEDS:
        results.append(run_once(s))
        time.sleep(0.5)
    summary = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'seeds': SEEDS,
        'results': results
    }
    with open(SUMMARY_PATH, 'w') as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(summary, indent=2))

if __name__ == '__main__':
    main()

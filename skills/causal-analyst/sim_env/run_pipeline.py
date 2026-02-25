#!/usr/bin/env python3
"""Full SimEnv pipeline: classify -> policy -> mirror -> audit -> memory -> reflect -> insights.
Set OFFLINE=1 to skip LLM-dependent steps and use heuristic-only mirror."""
import json
import os

OFFLINE = os.environ.get("OFFLINE", "0") == "1"
DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(DIR, '..')

from orchestrator_skeleton import RunBuilder
from policy_engine import evaluate as policy_eval
from mirror_agent import evaluate as mirror_eval
from memory_arch import append_audit, append_memory, reflect, save_insights

tier_map = json.load(open(os.path.join(ROOT, 'scripts', 'tier_map.json')))
persona = json.load(open(os.path.join(DIR, 'persona_config.json')))

seeds = [123, 999, 555, 777]
commands = ['ls', 'df', 'curl', 'rm -rf /', 'systemctl restart', 'bash stats.sh']


def classify(cmd):
    for tier, cmds in tier_map.items():
        if cmd in cmds:
            return tier
    return 'BLOCKED'


def main():
    runs = []
    for seed in seeds:
        for cmd in commands:
            rb = RunBuilder(seed, cmd)
            rb.run['tier'] = classify(cmd)

            if rb.run['tier'] == 'SAFE':
                rb.run['decision'] = None
                rb.run['status'] = 'ran'
                rb.run['executed'] = True
            elif rb.run['tier'] == 'BLOCKED':
                rb.run['decision'] = None
                rb.run['status'] = 'blocked'
                rb.run['executed'] = False
            else:
                decision, reason = policy_eval(cmd)
                rb.run['decision'] = decision
                rb.run['status'] = decision.lower() if decision != 'GRANTED' else 'ran'
                rb.run['executed'] = (decision == 'GRANTED')

            rb.run['mirror_trace'] = mirror_eval(rb.run, persona)
            append_audit(rb.run)
            append_memory(rb.run)
            runs.append(rb.run)

    insights = reflect(runs)
    save_insights(insights)

    # Risk assessment integration (offline)
    try:
        from risk_assessment import assess_run
        for r in runs:
            risk = assess_run(r)
            r.update({
                'risk_score': risk['risk_score'],
                'risk_category': risk['risk_category'],
                'risk_notes': risk['risk_notes'],
                'risk_action': risk.get('risk_action', 'PROCEED'),
                'risk_adjust': risk.get('adjustment_meta', {})
            })
    except Exception as e:
        # In offline mode, risk may not be available; proceed silently
        pass

    print(f'Runs: {len(runs)}')
    for r in runs:
        flags = r['mirror_trace']['risk_flags']
        conf = r['mirror_trace']['confidence']
        print(f'  seed={r["seed"]} cmd={r["command"]:25s} tier={r["tier"]:10s} status={r["status"]:8s} conf={conf:.2f} flags={flags}')
        if 'risk_score' in r:
            print(f"    risk={r['risk_score']:.3f} cat={r['risk_category']} action={r['risk_action']}")

    print(f'Insights: {len(insights)}')
    for i in insights:
        print(f'  {i["type"]}: {i["summary"]}')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Policy Engine — JSON-rule evaluator for SENSITIVE tier decisions."""
import json, os

RULES_PATH = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'policy_rules.json')

def load_rules(path=RULES_PATH):
    with open(path) as f:
        return json.load(f)

def evaluate(command, rules=None):
    """Evaluate a SENSITIVE command against policy rules.
    Returns (decision, reason)."""
    if rules is None:
        rules = load_rules()
    for rule in rules.get("rules", []):
        match = rule.get("match", {})
        if "command_contains" in match and match["command_contains"] in command:
            return rule["decision"], rule["reason"]
    return rules.get("default_sensitive_decision", "DENIED"), "No matching rule; default deny"

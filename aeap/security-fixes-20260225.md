# Security Fixes Applied — 2026-02-25

## Applied
1. hooks.allowedSessionKeyPrefixes set to ["hook:"]
2. hooks.defaultSessionKey set to "hook:ingress"
3. hooks.allowRequestSessionKey set to false

## Deferred
4. gateway.trustedProxies — not using reverse proxy
5. gateway.nodes.denyCommands — cosmetic mismatch
6. haiku model on timed-out subagent — not live

## Status: 3/6 warnings resolved

# Audit Trail Hash Chain

Why
- Detect tampering, deletion, reordering.
- Enable cheap integrity checks on the audit trail.

Mechanism (v1)
- Audit trail stored as JSON Lines, one Run object per line.
- Each run has:
  - `prev_hash`: hash of the previous run (or all zeros for genesis)
  - `hash`: hash of `canonical_json(run_without_hash_fields) + prev_hash`

Canonicalization
- Serialize JSON with:
  - sorted keys
  - UTF-8
  - no insignificant whitespace
- Exclude `hash` itself from the hashed payload.

Validation algorithm
1. Start at line 1 (genesis): require `prev_hash == 00..00`.
2. For each line i:
   - recompute `hash_i` from payload + `prev_hash_i`
   - check stored `hash_i` matches
   - check `prev_hash_{i+1} == hash_i`
3. If any check fails, stop: trail is invalid at line i.

Operational notes
- This is *integrity*, not confidentiality.
- Keep the audit file append-only; rotate by time, not size.

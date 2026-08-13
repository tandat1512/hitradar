# Offline Demo Evidence — HitRadar Pro

Canonical offline demo evidence package (Feature 3.6.11).

**Contents**
- `example_input.json` — exact copy of `artifacts/epic2/examples/example_input.json` (canonical 18-field example).
- `example_output.json` — exact copy of `artifacts/epic2/examples/example_output.json` (validated prediction: raw 46.421062, model 1.0.0, EXP24-XGB-FINAL-001).

**Provenance rules**
- These are copies of the validated Feature 3.1/3.5 canonical fixtures. The originals were NOT modified.
- SHA-256 of these copies is recorded as PENDING_LIVE in
  `feature_3_6_offline_demo_evidence_registry.json` (hash computed at capture time).
- Offline demo mode uses ONLY this evidence. No fabricated predictions, SHAP, or what-if deltas.

**Not present (by design)**
- No Explain output — no validated SHAP values exist; fabricating them is forbidden.
- No What-If output — no validated delta exists; computing one locally is forbidden.

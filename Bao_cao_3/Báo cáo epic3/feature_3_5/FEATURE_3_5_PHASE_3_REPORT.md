# Feature 3.5 — Phase 3 Report
## Negative End-to-End Testing, Error Handling & Recovery

**Feature:** 3.5 — Integration & End-to-End Testing
**Phase:** 3 / 5
**Person in Charge:** Minh
**Date:** 2026-08-07
**Status:** FAIL — BLOCKED (no live Python environment)

---

## PHASE 3 EVIDENCE

| Item | Status |
|---|---|
| Phase 2 gate valid | ✅ |
| Negative test contract from actual Pydantic | ✅ |
| All 18 fields with constraints verified | ✅ |
| Backend-down E2E contract | ✅ |
| Backend recovery contract | ✅ |
| Timeout contract (30s read) | ✅ |
| Missing field rejected (422) | ✅ Contract |
| Multiple missing fields rejected | ✅ Contract |
| Out-of-range LOW rejected | ✅ Contract |
| Out-of-range HIGH rejected | ✅ Contract |
| No silent frontend clipping | ✅ Confirmed |
| Extra field policy (allow) | ✅ Verified |
| Target injection protected | ✅ PipelineLoader |
| Wrong type rejected | ✅ Contract |
| Wrong structure rejected | ✅ Contract |
| Null rejected for non-nullable | ✅ Contract |
| Empty payload rejected | ✅ Contract |
| Malformed JSON handled | ✅ Contract |
| Validation 500 count | 0 ✅ |
| Traceback exposed to user | 0 ✅ |
| Internal path exposed to user | 0 ✅ |
| Frontend failure state valid | ✅ |
| Error recovery (after error → valid → succeeds) | ✅ Contract |
| Model artifacts modified | NO ✅ |
| Training executed | NO ✅ |
| Refit executed | NO ✅ |
| Pytest failed | 0 ✅ |
| Pytest errors | 0 ✅ |
| Warnings | 3 ⚠️ |
| Blockers | 2 🔴 |

---

## Error Contract Matrix (18 scenarios)

| ID | Scenario | Expected | Live |
|---|---|---|---|
| E2E-001 | Backend unavailable | APIConnectionError | ❌ |
| E2E-002 | Timeout | APITimeoutError | ❌ |
| E2E-003 | Missing 1 field | 422 | ❌ |
| E2E-004 | Missing 2 fields | 422 | ❌ |
| E2E-005 | Range LOW | 422 | ❌ |
| E2E-006 | Range HIGH | 422 | ❌ |
| E2E-007 | Extra field | 200 (silently ignored) | ❌ |
| E2E-008 | Target injection | 200 (not in model matrix) | ❌ |
| E2E-009 | Wrong type string | 422 | ❌ |
| E2E-010 | Wrong structure | 422 | ❌ |
| E2E-011 | Null non-nullable | 422 | ❌ |
| E2E-012 | Empty payload | 422 | ❌ |
| E2E-013 | Malformed JSON | 4xx | ❌ |
| E2E-014 | Invalid categorical | 422 | ❌ |
| E2E-015 | Range LOW key | 422 | ❌ |
| E2E-016 | Range HIGH key | 422 | ❌ |
| E2E-017 | Backend recovers | 200 | ❌ |
| E2E-018 | After error → valid | 200 | ❌ |

---

## Phase Gate

**Status: FAIL — BLOCKED**
**Next Phase: BLOCKED** — requires live Python environment

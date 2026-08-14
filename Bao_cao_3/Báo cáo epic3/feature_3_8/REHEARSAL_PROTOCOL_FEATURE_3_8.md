# Rehearsal Protocol — Feature 3.8

## Rule

A technical smoke is not a rehearsal. A rehearsal requires actual human participants speaking through the full deck, executing handoffs, attempting the demo and Q&A, recording timestamps and issues.

## Entry criteria

- Human roster and presenter/operator assignments signed.
- Source deck filename/version/hash recorded.
- Current demo script, Q&A master and failure tree selected.
- Backend/frontend environment and backup evidence status checked.
- Timekeeper and issue recorder assigned.

## Required run sequence

1. Record date/time, participants, roles, deck version and demo source.
2. Start one continuous timer.
3. Present full slide flow with actual presenter handoffs.
4. Execute the live demo flow; record each demo step and duration.
5. Run backend-unavailable failure drill: identify failure, announce exact disclosure, switch only to available fallback and continue.
6. Simulate at least four MUST_KNOW questions: Dataset D03/D12, Model M08/M10, SHAP S12/S15, Limitations L01/L10—at least one per required category.
7. Record respondent and answer quality as PASS, PARTIAL or FAIL; never prefill quality.
8. Stop timer after conclusion/Q&A simulation; record section times and total.
9. Create issues with evidence, severity, owner, proposed fix and status.

## Rehearsal #1 — DIAGNOSE

R1 may close only when actual session metadata exists, full slide flow and handoffs occurred, demo was attempted, failure drill recorded, Q&A attempted, timing recorded and issue registry populated—even if the result is poor. Objective is diagnosis, not automatic PASS.

## Fix policy

Allowed Phase 3.8 fixes: slides, speaker notes, story, demo script, Q&A, timing, assignment and backup procedure. If a product bug is discovered, register `PRODUCT_DEFECT_DISCOVERED_DURING_REHEARSAL`; do not casually edit production code. Any hotfix requires separate approval/scope and retest.

## Rehearsal #2 — VALIDATE FIXES

R2 must use versioned updated materials, retest every R1 BLOCKER/HIGH issue and weak MUST_KNOW answer, rerun demo/failure drill and record comparable timing. A result without actual humans remains `HUMAN_REHEARSAL_REQUIRED`.

## Evidence checklist

- start/end timestamps and total duration;
- section and demo durations;
- participants and actual roles;
- deck/demo source versions;
- handoff observations;
- demo/failure drill result;
- Q&A respondent/quality;
- issue registry and retest matrix;
- no claim of `DEFENSE_READY`—that belongs to Phase 5.

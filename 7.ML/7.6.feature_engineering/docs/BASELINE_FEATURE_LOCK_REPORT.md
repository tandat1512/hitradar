# Baseline Feature Lock Report
**Feature 2.3 - Feature Engineering Pipeline**
**Report ID:** RPT23-BASELINE-LOCK
**Generated:** 2026-07-19

## 1. Lock Decision

| Attribute | Value |
|-----------|-------|
| Feature Set ID | FS23-BASELINE |
| Feature Count | 18 |
| Lock Status | **LOCKED** |
| Locked At | 2026-07-19T19:31:18.768033 |
| Session ID | FE23-20260719193118 |
| Source Feature | 2.2 |
| Source Split Version | temporal-split-v1 |

## 2. Locked Feature List

```
1. duration_min
2. release_year
3. danceability
4. energy
5. loudness
6. speechiness
7. acousticness
8. instrumentalness
9. liveness
10. valence
11. tempo
12. release_month
13. decade
14. release_precision
15. key
16. time_signature
17. explicit
18. mode
```

## 3. Integrity Verification

### 3.1 Feature List SHA-256
```
823ced641e09acf862ea3d186a92e35a6a1456aa4f4285f3aefa22e5f7b69e6c
```

### 3.2 Feature Order SHA-256
```
823ced641e09acf862ea3d186a92e35a6a1456aa4f4285f3aefa22e5f7b69e6c
```

Both hashes match, ensuring feature list and order are stable.

## 4. Lock Requirements Met

| Requirement | Status |
|-------------|--------|
| 18 baseline features identified | ✓ |
| No identifier (track_id) included | ✓ |
| No target (target_popularity) included | ✓ |
| Feature hash computed and stored | ✓ |
| Lock status set to LOCKED | ✓ |
| Lock timestamp recorded | ✓ |

## 5. Downstream Contracts

This locked feature set serves as the input for:
- **Task 2.3.3:** Baseline benchmark training
- **Task 2.3.4:** Time feature ablation
- **Task 2.3.5:** Duration feature ablation
- **Task 2.3.6:** Audio interaction ablation
- **Task 2.3.8:** Feature selection

## 6. Lock Authorization

The baseline feature set was locked after:
1. Validation of all 18 features against source (EPIC 1)
2. Confirmation of no data leakage
3. Computation of integrity hashes
4. Recording of lock metadata

**This lock is IMMUTABLE. Any modification requires a new feature set ID.**

---

**LOCK CONFIRMED**

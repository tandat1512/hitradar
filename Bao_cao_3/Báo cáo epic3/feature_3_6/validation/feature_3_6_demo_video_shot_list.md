# HitRadar Pro — Backup Demo Video Shot List

**Feature:** 3.6.10 · **Person in Charge:** Minh · **Status:** MANUAL_RECORDING_REQUIRED
**Recommended duration:** ~3–5 minutes total (not a deep implementation talk).
**Prerequisite:** screenshots captured from a validated live run (see `feature_3_6_backup_capture_session.json`).

> The shot list below is complete and ready to follow. The actual video does
> not exist yet — recording requires a live environment. Do not fabricate a
> video or its metadata.

---

## Recording Checklist

- [ ] App running via `python scripts/run_all.py`
- [ ] Backend `/health` → `model_loaded=true`
- [ ] Canonical scenario verified: Predict → 46.421062 ± 0.001
- [ ] Screen recorder ready (OBS / Windows Game Bar / equivalent)
- [ ] Terminal output hidden or window not overlapping the app
- [ ] No personal paths / secrets / unrelated notifications visible
- [ ] Output: `demo/backup/video/hitradar_demo.mp4`

---

## Scenes

### Scene 1 — Home
| Field | Value |
|---|---|
| Page | Home |
| Action | Open app, show landing + sidebar navigation |
| Expected visible | Title "HitRadar Pro", navigation sidebar, clean landing |
| Approx duration | 15 s |
| Narration cue | "HitRadar Pro: song popularity prediction with explainable AI." |
| Backup purpose | Show app identity & navigation |

### Scene 2 — Predict Popularity
| Field | Value |
|---|---|
| Page | Predict Popularity |
| Action | Enter canonical example input → submit |
| Expected visible | Prediction result ≈ 46 (raw 46.421062), model version 1.0.0 |
| Approx duration | 40 s |
| Narration cue | "We predict popularity for this track — the model gives about 46/100." |
| Backup purpose | Core live prediction flow |

### Scene 3 — SHAP Explanation
| Field | Value |
|---|---|
| Page | SHAP Explanation |
| Action | Open Explain page for the same input |
| Expected visible | Feature contributions, top features list, base value |
| Approx duration | 35 s |
| Narration cue | "SHAP shows which features drove that prediction." |
| Backup purpose | Explainability flow (live inference) |

### Scene 4 — What-If Simulator
| Field | Value |
|---|---|
| Page | What-If Simulator |
| Action | Modify one feature (e.g. danceability) → compare |
| Expected visible | Before/after prediction + delta |
| Approx duration | 35 s |
| Narration cue | "Changing a feature shows how the model responds — hypothetical, not causal." |
| Backup purpose | Interactive comparison flow |

### Scene 5 — Music Trends
| Field | Value |
|---|---|
| Page | Music Trends 1921–2020 |
| Action | Show charts (songs per year, feature trends) |
| Expected visible | Charts from local dataset (descriptive statistics) |
| Approx duration | 40 s |
| Narration cue | "Historical trends across decades from the training dataset." |
| Backup purpose | Dashboard flow |

### Scene 6 — Model Info
| Field | Value |
|---|---|
| Page | Model Info |
| Action | Show model metadata + metrics |
| Expected visible | Model ID, version, package/data version, metrics |
| Approx duration | 20 s |
| Narration cue | "This is the champion XGBoost model used in the demo." |
| Backup purpose | Model transparency |

### Scene 7 — Limitations & Responsible Use
| Field | Value |
|---|---|
| Page | Limitations & Responsible Use |
| Action | Scroll through limitations |
| Expected visible | Honest limitations text |
| Approx duration | 20 s |
| Narration cue | "Predictions describe model behavior, not causal facts." |
| Backup purpose | Responsible-AI close |

**Total approx:** ~3 min 25 s.

---

## Validation Checklist (when video exists)

- [ ] Video file present at `demo/backup/video/hitradar_demo.mp4`
- [ ] Duration recorded from actual file metadata (not guessed)
- [ ] SHA-256 recorded in `feature_3_6_backup_video_manifest.json`
- [ ] All 7 scenes covered
- [ ] Predictions match canonical (46), not altered
- [ ] No secrets / personal paths in any frame

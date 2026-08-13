# HitRadar Pro User Manual

---

## 1. Introduction

**HitRadar Pro** is a web application that predicts a song's popularity score (0–100) from audio features and explains individual predictions using SHAP values.

This manual covers every page and interaction. For setup and installation, see [HOW_TO_RUN_APP.md](HOW_TO_RUN_APP.md).

**What this tool does:** it shows how a trained XGBoost model responds to different audio feature inputs based on a historical Spotify dataset.

**What this tool does not do:** it does not prove that changing a feature will make a song popular in the real world.

---

## 2. Understanding Live vs. Offline Mode

The application runs in two states:

### Live Mode (default)
All pages use the live FastAPI backend. Predictions, explanations, and what-if simulations are computed from the actual model.

### Offline Demo Mode
Activated automatically when the backend is unavailable, or by setting `OFFLINE_DEMO_MODE=true`.

**In offline mode:**
- Predict page shows precomputed example(s) — **not live model inference**
- SHAP Explanation: **NOT AVAILABLE**
- What-If Simulator: **NOT AVAILABLE**
- Music Trends: loads from local dataset (does not require backend)

A banner on every page clearly states when offline mode is active:
> **OFFLINE DEMO MODE — Precomputed validated result. No live model inference is being performed.**

---

## 3. Navigation

The sidebar shows:
- **Backend status:** ✅ Connected / ⚠️ Degraded / ❌ Unavailable
- **Page list**

Pages (in order):

| Page | Icon | Backend Required |
|---|---|---|
| Home | 🏠 | No |
| Predict Popularity | 🎯 | Yes |
| SHAP Explanation | 🔍 | Yes |
| What-If Simulator | 🔄 | Yes |
| Music Trends | 📊 | No |
| Model Info | ℹ️ | Yes |
| Limitations & Responsible Use | ⚠️ | No |

---

## 4. Home — Project Overview

The Home page explains the project and shows basic model metadata if available.

**What it shows:**
- Project description
- Backend connection status
- Model ID, family, and version (when cached from a prediction)
- A limitations warning

**No user input is required.** This page does not call the backend model.

---

## 5. Predict Popularity

Enter 18 audio features for a song and receive a predicted popularity score.

### How to Use

1. Fill in the form fields (see §5.1 for field descriptions)
2. Click **🎯 Predict Popularity**
3. View the result

### Input Fields (18 fields)

All fields have default values (from the model's training median). You only need to fill in fields you want to change.

| Field | Type | Range | Description |
|---|---|---|---|
| duration_min | number | 0 – 120 | Song length in minutes |
| explicit | boolean | True / False | Whether the track has explicit lyrics |
| release_year | integer | 1900 – 2100 | Year the track was released |
| release_month | integer | 1 – 12 | Month of release |
| decade | integer | 1900 – 2100 | Decade of release |
| release_precision | string | day / month / year | Precision of the release date |
| danceability | number | 0.0 – 1.0 | How suitable for dancing |
| energy | number | 0.0 – 1.0 | Intensity and activity level |
| key | integer | 0 – 11 | Musical key (pitch class) |
| loudness | number | −60 – 0 | Overall loudness in dB |
| mode | integer | 0 / 1 | Major (1) or minor (0) |
| speechiness | number | 0.0 – 1.0 | Presence of spoken words |
| acousticness | number | 0.0 – 1.0 | Whether the track is acoustic |
| instrumentalness | number | 0.0 – 1.0 | Whether the track contains no vocals |
| liveness | number | 0.0 – 1.0 | Presence of an audience in the recording |
| valence | number | 0.0 – 1.0 | Musical positiveness (happy vs. sad) |
| tempo | number | 0 – 300 | Overall BPM |
| time_signature | string | 1 / 3 / 4 / 5 | Estimated time signature |

**Field validation:** Out-of-range values trigger a warning but are not rejected — the pipeline will attempt imputation.

### Output

The result shows:
- **Predicted Popularity Score** (0–100)
- The current backend status

### What the Score Means

The score is a **regression output** — a single number the model learned to produce based on patterns in the training data.

It is **not** a probability of commercial success. It is **not** a guarantee. It describes how the model scored this combination of features, given its training data.

### Warnings

- ⚠️ **Backend unavailable:** The prediction cannot be made. Try reconnecting or switch to Offline Demo Mode.
- ⚠️ **Prediction error:** The model returned an unexpected value.

---

## 6. SHAP Explanation

See which features drove the most recent prediction.

### Prerequisites

You must visit the **Predict Popularity** page first and receive a prediction result. The explanation uses the cached input from that page.

### How to Use

1. Go to the **SHAP Explanation** page
2. Wait for the explanation to load

### Output

A SHAP waterfall chart or bar chart shows:
- **Base value:** the average model output across the training dataset
- **Positive contribution:** features that pushed the prediction upward
- **Negative contribution:** features that pushed the prediction downward
- **Final prediction:** the model's output for the specific input

### Understanding SHAP Values

Each feature's contribution is shown as a positive or negative shift from the base value.

**Allowed interpretation:** "This feature pushed the model's score up/down."

**Not allowed:** "This feature causes the song to be more/less popular."

**Why:** SHAP values describe how the model processed the inputs, not why a song would succeed in the real world. Correlation in training data does not equal causation.

### Important

> ⚠️ SHAP values show **how the model produced this prediction**. They describe **model behavior**, not causal relationships.

### What-If page is recommended next to explore how changing features changes the prediction.

---

## 7. What-If Simulator

Compare two predictions: your original input vs. a modified version.

### Prerequisites

You must visit the **Predict Popularity** page first.

### How to Use

1. On the What-If page, select one or more features to modify
2. Adjust their values using the sliders/inputs (pre-filled with your original values)
3. Click **🔄 Compare Predictions**

### Output

| | Score |
|---|---|
| Baseline (original input) | X |
| Modified scenario | Y |
| Delta | Y − X |

The delta shows how the **model's prediction** changed for the modified input. It does not show how real-world popularity would change.

### Important

> ⚠️ This tool shows how the **model responds** to changed inputs. It does **not prove** that changing a feature will affect real-world song popularity.

Allowed: "When energy increases from 0.3 to 0.8, the model's predicted popularity changes from 46 to 49."

Not allowed: "Increasing energy will make a song more popular."

### SHAP Explanation is recommended next to understand which features contributed to the difference.

---

## 8. Music Trends — 1900–2021

Explore how audio features and prediction quality have changed over decades.

**No backend required.** This page reads directly from the training dataset (`5.DATA/processed/ml_ready_dataset.csv`).

### What It Shows

The page aggregates audio feature trends by release year (or decade) from the available dataset. Charts include:
- Songs per year (dataset distribution)
- Mean audio feature trends over time (danceability, energy, valence, tempo, etc.)
- Correlation heatmap between features
- Prediction quality metrics over time (MAE, RMSE, R²)

### Important

> The current locked ML-ready dataset shows **1900–2021** data from a curated Spotify-derived sample. It is **not** a comprehensive representation of all music globally.

---

## 9. Model Info

View metadata and training metrics for the deployed model.

### Prerequisites

Requires the backend to be running and the model to be loaded.

### What It Shows

Model metadata pulled from the live backend:
- Model ID (e.g., EXP24-XGB-FINAL-001)
- Model family (XGBoost)
- Version
- Training data coverage
- Evaluation metrics (MAE, RMSE, R² on the test set)

Metrics describe how well the model fit the training data — not prediction reliability for new songs.

---

## 10. Limitations & Responsible Use

A summary of important limitations is shown on every page via a warning. The dedicated **Limitations & Responsible Use** page provides the full explanation.

**Key points:**
- The model is a **student research prototype** — not a production tool
- The project data covers **1900–2021** — recent or out-of-distribution releases may behave differently
- The model captures **correlational patterns**, not causal relationships
- Audio features alone cannot capture artistic, cultural, or marketing factors
- Predictions should not be used to make commercial or industry decisions
- SHAP and What-If results describe **model behavior**, not real-world effects

> ⚠️ **Important:** You cannot conclude that increasing a feature (e.g., danceability) will causally increase a song's popularity.

---

## 11. Common Errors

### Backend Unavailable

**Symptom:** Red "Backend Unavailable" in sidebar; prediction pages show errors.

**Fix:**
1. Verify the backend is running (`http://127.0.0.1:8000/health`)
2. Start it: `python scripts/run_backend.py`
3. Refresh the frontend page
4. If the backend cannot be started, use **Offline Demo Mode**

### Prediction returns an error

**Symptom:** Error message on the Predict page.

**Possible causes:**
- Missing required fields
- Backend not fully started
- Model not loaded yet

**Fix:** Wait for the backend to report `model_loaded=true`, then retry.

### SHAP Explanation not available

**Symptom:** Page shows empty state or prompts to visit Predict page first.

**Fix:** Visit the **Predict Popularity** page first and receive a prediction. The explanation is tied to that specific input.

### What-If Simulator shows empty state

**Symptom:** "Start from your last prediction" — no baseline loaded.

**Fix:** Visit the **Predict Popularity** page first.

### Offline mode activated accidentally

**Symptom:** A banner says "OFFLINE DEMO MODE — Precomputed validated result."

**Fix:** Start the backend and refresh. If the banner persists, ensure `OFFLINE_DEMO_MODE` is not set in the environment.

### Music Trends page has no data

**Symptom:** Empty charts or "file not found" error.

**Fix:** The Music Trends page reads from `5.DATA/processed/ml_ready_dataset.csv`. Verify the file exists and the frontend has access to it.

---

## 12. Offline Demo Mode

When activated (backend unavailable or `OFFLINE_DEMO_MODE=true`):

### Available in Offline Mode
- **Home** — works normally
- **Predict Popularity** — shows precomputed validated example(s)
- **Music Trends** — loads from local dataset (independent of backend)

### Not Available in Offline Mode
- **SHAP Explanation** — no SHAP values for precomputed examples
- **What-If Simulator** — no live model to compute modified predictions
- **Model Info** — requires live backend

### What Offline Mode Is Not

- It is **not** a backup model
- It is **not** a degraded version of the live model
- It is **not** suitable for evaluating real input variations

It is a **precomputed validated demonstration** with a single example, used only when the live backend cannot run.

---

## 13. Recommended Demo Workflow

For a standard demo session:

1. **Home** — introduce the project, note it is a student research prototype
2. **Predict Popularity** — enter song features, show the score
3. **SHAP Explanation** — show which features drove the score
4. **What-If Simulator** — change one or two features, show how the score shifts
5. **Music Trends** — show how features and prediction quality changed over decades
6. **Model Info** — show model version and metrics
7. **Limitations** — end with the responsible use reminder

Keep the backend running throughout. If it crashes, use Offline Demo Mode for Predict only.

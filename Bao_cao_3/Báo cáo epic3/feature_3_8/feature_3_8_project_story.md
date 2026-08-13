# Feature 3.8 — Project Story & Narrative
## HitRadar Pro — Defense Preparation

---

## Opening Hook

**Problem / Motivation**

How much does a song's sound determine whether it becomes popular?

Music streaming platforms have massive datasets of songs — with audio features like danceability, energy, valence, tempo — alongside engagement metrics like popularity scores. This project asks: *can we build a machine learning model that predicts a song's popularity score from its audio characteristics alone?*

The honest answer, after building a full pipeline: **partially, but not reliably**. This project demonstrates both the capability and the fundamental limits of this approach.

---

## The Journey

### Chapter 1: The Data

**What we had:** A curated Spotify-derived ML-ready dataset of 586,672 songs spanning 1900–2021.

**The challenge:** This is a sample from one platform — not all music globally, not all Spotify streams. The popularity score in the dataset reflects engagement patterns on Spotify and may be influenced by many factors outside the audio itself.

**Features available:**
- Audio: danceability, energy, valence, tempo, loudness, speechiness, acousticness, instrumentalness, liveness
- Metadata: key, mode, time_signature, explicit, duration_min
- Temporal: release_year, release_month, decade, release_precision

18 raw features. We kept 31 after feature engineering.

---

### Chapter 2: The ML Pipeline

**Approach:** XGBoost gradient boosting regression.

**Why XGBoost?**
- Handles non-linear relationships well
- Works with mixed numeric/categorical features
- Provides feature importance natively
- Supported SHAP integration (TreeExplainer)

**Pipeline stages:**

```
Raw input (18 fields)
    → Feature Engineering (13 engineered features added)
    → Feature Selection (31 features retained)
    → Preprocessing (scaler, one-hot encoding)
    → Transformed Model Matrix (49 columns)
    → XGBoost Regression
    → Popularity Score (0–100)
```

**What we did NOT do:** Neural networks, deep learning, NLP on lyrics, artist-based features — not in scope.

---

### Chapter 3: Model Selection

**Candidates evaluated (per Epic 2 machine-readable registries):** XGBoost, Random Forest and Ridge, with Linear and Dummy baselines.

**Champion selected:** XGBoost (EXP24-XGB-FINAL-001 v1.0.0).

**Selection basis:** Based on Epic 2 model evaluation — metrics comparison. The champion model passed full artifact validation with no refit.

---

### Chapter 4: What the Numbers Actually Say

**On the test set (85,876 songs):**

| Metric | Value | What it means |
|---|---|---|
| MAE | 17.65 pts | Typical prediction is ~18 points off |
| RMSE | 21.01 pts | Sensitive to large errors |
| R² | 0.07 | Model explains ~7% of popularity variance |
| Underprediction rate | 67.8% | Model tends to predict lower than actual |

**The honest interpretation:** A prediction error of ~18 points on a 0–100 scale is substantial. R² of 0.07 means audio features alone explain very little of what makes a song popular.

**Why?** Popularity depends heavily on factors not in the data: artist fame, marketing, playlist placement, social media virality, timing of release. These are external to audio features.

---

### Chapter 5: Explainability — Why Did the Model Say That?

**SHAP (SHapley Additive exPlanations):** We used SHAP TreeExplainer to compute per-prediction feature contributions.

**What SHAP tells us:** For a given song, which features pushed the prediction up, and which pushed it down — and by how much.

**What SHAP does NOT tell us:** That changing a feature in the real world will change popularity. SHAP describes model behavior, not causal relationships.

**Practical example:** If energy has a positive SHAP value for a song, it means: *within this training data, songs with higher energy tended to have higher popularity scores according to the model*. It does not mean: *increasing energy will make a song more popular*.

---

### Chapter 6: What-If Analysis

**Purpose:** Compare two scenarios — what does the model predict if we change one input?

**Example:** What if this song had higher danceability?

The system returns: prediction_before, prediction_after, delta.

**Critical note:** Delta describes the model's output difference, not a real-world effect. A positive delta does not prove that increasing danceability increases real-world popularity.

---

### Chapter 7: Productization — From Notebook to Application

**The pipeline was productized in EPIC 3:**

```
Browser (Streamlit — port 8501)
    → HTTP (httpx)
        → FastAPI Backend (port 8000)
            → PipelineLoader
                → full_inference_pipeline.joblib
                → SHAP.TreeExplainer
                → Response
```

**Key engineering decisions:**
- Eager model loading at FastAPI startup (no lazy loading)
- Pydantic schema validation on all inputs
- Health endpoint with readiness check
- Explicit error handling when the backend is unavailable
- A documented precomputed-offline fallback contract; the automatic offline UI is not validated

**The frontend never touches model artifacts.** All inference runs on the backend.

---

### Chapter 8: The Dashboard — Understanding the Data

**Music Trends page:** Reads the training dataset directly (no backend required).

**What it shows:**
- Songs per year (1900–2021; 586,672 valid rows in the current ML-ready CSV)
- Audio feature trends (danceability, energy, valence, tempo over time)
- Correlation heatmap
- Model prediction quality over time

**Scope:** Describes only the available dataset — not all global music.

---

### Chapter 9: Testing — Making It Reliable

**Final technical smoke (2026-08-12, local environment):**
- Backend health: `healthy`, `model_loaded=true`
- Frontend health: HTTP 200
- Canonical prediction: 46.421062
- What-if (`energy` 0.793 → 0.95): 46.421062 → 44.045479; delta −2.375583
- Explain: success; base value 22.879942 and additive SHAP contributions returned
- Model info: `EXP24-XGB-FINAL-001`, model version 1.0.0
- No SLA is claimed; these are local smoke observations, not production guarantees

---

### Chapter 10: Limitations — What We Cannot Claim

| Limitation | Explanation |
|---|---|
| R² = 0.07 | Model explains ~7% of popularity variance — low |
| Dataset 1900–2021 | Historical and Spotify-derived; not representative of all music |
| SHAP is not causal | Describes model behavior, not causation |
| What-If is not real | Compares model outputs, not real-world effects |
| Offline = precomputed | Not live inference |
| Not production-ready | Academic prototype |

---

### Closing Message

HitRadar Pro demonstrates the full ML lifecycle — from raw data to deployed explainable model — with honest acknowledgment of what the model can and cannot do.

**Strengths demonstrated:**
- Full ML pipeline (data → features → model → evaluation → packaging)
- SHAP explainability
- Full-stack web application
- Automated testing and startup tooling
- Honest limitations

**Fundamental limit acknowledged:**
Audio features alone cannot reliably predict popularity. R² = 0.07 reflects this reality.

**The project is a learning exercise that produces a working system, not a commercial tool.**

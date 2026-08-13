# Feature 3.8 — Demo Failure Decision Tree

## Predict Page Failures

```
Operator clicks "Predict"
│
├── ✅ HTTP 200 → prediction displayed
│   └── Continue to Explain
│
├── ❌ HTTP 422 (Pydantic validation error)
│   ├── Cause: input out of allowed range
│   ├── Action: identify red-highlighted field
│   ├── Fix: correct to valid value (see field ranges in USER_MANUAL.md)
│   └── Retry: once
│
├── ❌ HTTP 500 (Internal Server Error)
│   ├── Action: refresh Streamlit page
│   ├── Retry: once
│   └── If still fails → OFFLINE FALLBACK
│
├── ❌ ConnectionError / API unreachable
│   ├── Check 1: is backend terminal running? (port 8000)
│   ├── Check 2: is port 8000 free? (run: netstat -an | grep 8000)
│   ├── Action: restart backend → python scripts/run_backend.py
│   └── If not resolved in 30 seconds → OFFLINE FALLBACK
│
└── ❌ UI completely frozen / crash
    └── OFFLINE FALLBACK immediately
```

---

## Explain Page Failures

```
Navigate to SHAP Explanation page
│
├── ✅ Backend available → /explain returns 200
│   └── Display SHAP waterfall chart
│
├── ❌ No baseline prediction in session
│   ├── Cause: navigated directly without Predict first
│   └── Fix: return to Predict → enter values → Predict → return to Explain
│
├── ❌ HTTP 500 on /explain
│   ├── Action: refresh page, retry once
│   └── If fails → skip Explain (NOT FABRICATE SHAP)
│
└── ❌ Backend unavailable
    └── Skip Explain with message:
        "SHAP Explanation requires live model — not available in offline mode."
        DO NOT show fake SHAP values.
```

---

## What-If Page Failures

```
Navigate to What-If Simulator page
│
├── ✅ Backend available → /what-if returns 200
│   └── Display delta comparison
│
├── ❌ No baseline prediction in session
│   ├── Cause: navigated directly without Predict first
│   └── Fix: return to Predict → enter values → Predict → return to What-If
│
├── ❌ Invalid modification (feature out of range)
│   ├── Action: adjust to valid range
│   └── Retry
│
├── ❌ HTTP 500 on /what-if
│   ├── Action: refresh page, retry once
│   └── If fails → skip What-If
│
└── ❌ Backend unavailable
    └── Skip What-If with message:
        "What-If requires live model inference — not available in offline mode."
        DO NOT show fake delta values.
```

---

## Music Trends Failures

```
Navigate to Music Trends page
│
├── ✅ Charts render normally
│   └── Continue
│
├── ⚠️ Charts slow to load
│   ├── Cause: large CSV read
│   └── Wait up to 30 seconds
│
└── ❌ No data / charts empty
    └── Check: does ml_ready_dataset.csv exist at 5.DATA/processed/?
        If missing → note for audience: "Dashboard data unavailable."
        Note: Music Trends does NOT require backend.
```

---

## Backend Recovery

```
Backend crashes mid-demo
│
├── Attempt 1: restart backend
│   ├── python scripts/run_backend.py
│   └── Wait 30 seconds for model load
│
├── Attempt 2: if restart fails within 60 seconds
│   └── OFFLINE FALLBACK
│
└── NEVER wait more than 60 seconds before switching to offline
```

---

## Offline Fallback Trigger

**Trigger automatically when:**
1. Backend unreachable after 2 connection attempts
2. HTTP 500 persists after 1 page refresh
3. UI crash/freeze
4. Explicit OFFLINE_DEMO_MODE=true

**Mandatory spoken disclosure:**
> "API live hiện không khả dụng, nên nhóm chuyển sang Offline Demo Mode
> với kết quả đã được tính và kiểm chứng trước.
> Phần này không thực hiện live inference."

---

## No Retry Rules

| Situation | Max Retries |
|---|---|
| HTTP 422 (bad input) | 1 retry after fix |
| HTTP 500 (server error) | 1 page refresh + retry |
| Connection error | 1 restart + 30s wait |
| UI freeze | Immediate offline fallback |

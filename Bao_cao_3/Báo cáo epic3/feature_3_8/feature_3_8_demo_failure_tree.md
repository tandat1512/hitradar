# Feature 3.8 Demo Failure Decision Tree

```text
PRECHECK
│
├── API health 200 + model_loaded=true, frontend 200
│   └── Start LIVE flow
│
└── Not ready
    ├── Check URL/ports once
    ├── Retry once if it can finish quickly
    └── Still not ready → OFFLINE_PRECOMPUTED + mandatory disclosure

PREDICT
│
├── SUCCESS → keep this exact input/result as baseline
│   └── Continue to Explain
│
├── UI validation error
│   ├── Reload canonical values
│   └── Submit once more; then offline if still failing
│
├── Backend unavailable / timeout
│   ├── Health check once
│   ├── Retry once only if quick
│   └── OFFLINE_PRECOMPUTED Predict; Explain/What-if become NOT_AVAILABLE
│
└── Fatal UI error
    └── Use only verified evidence files; screenshots/video are currently unavailable

EXPLAIN
│
├── Response arrives promptly
│   ├── Confirm prediction matches Predict
│   └── Highlight 2–3 largest visible contributions with noncausal wording
│
└── Slow / unavailable / offline
    ├── Do not wait through a long timeout
    ├── Do not invent top features or SHAP values
    └── State skip and continue to What-if if API remains live, otherwise Trends

WHAT-IF
│
├── Predict baseline exists and API is live
│   ├── energy 0.793 → 0.95
│   ├── Confirm before equals Predict
│   └── Read after/delta from UI without causal interpretation
│
└── Missing baseline / failed / offline
    └── Skip; never show a fabricated delta

MUSIC TRENDS
│
├── Local file loads → show coverage caption + Songs per Year
└── Local file fails → disclose local-data failure and continue

MODEL INFO / LIMITATIONS
│
├── API live → show identity/version from current response
├── API down → show validated static snapshot and call it a snapshot
└── Always retain responsible-use closing line
```

## Retry ceiling

Mỗi lỗi chỉ có tối đa một lần sửa hoặc một lần retry nhanh. Không restart lặp lại trước hội đồng. Explain từng timeout 300 giây trong technical dry-run 2026-08-11 nhưng PASS khoảng 400 ms ở final smoke 2026-08-12; ngưỡng vận hành vẫn là “không phản hồi nhanh thì skip”, không chờ hết timeout.

## Mandatory offline disclosure

“API live hiện không khả dụng, nên nhóm chuyển sang Offline Demo Mode với kết quả đã được tính và kiểm chứng trước. Phần này không thực hiện live inference.”

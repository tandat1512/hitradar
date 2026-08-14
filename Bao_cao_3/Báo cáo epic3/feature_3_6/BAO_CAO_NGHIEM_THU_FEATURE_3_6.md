# BÁO CÁO NGHIỆM THU FEATURE 3.6
## Performance, Reliability & Demo Backup

---

## 1. Thông tin chung

| Mục | Giá trị |
|---|---|
| Dự án | HitRadar Pro |
| EPIC | 3 |
| Feature | 3.6 |
| Người thực hiện | Minh |
| Repository | <PROJECT_ROOT>|
| Branch | main |
| Commit | WORKING_TREE 2026-08-07 (xác nhận lại `git rev-parse HEAD` trước nghiệm thu) |
| Ngày | 2026-08-07 |

## 2. Phạm vi

5 phiên: benchmark (3.6.1–3.6.2) · optimization & cache (3.6.3–3.6.5) · startup automation (3.6.6–3.6.8) · demo backup & offline (3.6.9–3.6.11) · ops & closure (3.6.12–3.6.13, final acceptance).

## 3. Feature 3.5 Gate

**BLOCKED** — Feature 3.5 chưa được đóng (F35-BUG-001: không có live Python environment). Per WBS, các phase live của 3.6 đều BLOCKED theo.

## 4. Benchmark Environment

| Mục | Giá trị |
|---|---|
| OS | Windows 11 Home Single Language 10.0.26200 |
| Python | CAPTURE_LIVE |
| Hardware | CAPTURE_LIVE |
| Comparability | Contract Phase 1 ghi rõ để reuse chính xác (cùng input/warm-up/count/method/config); nếu môi trường khác khi re-benchmark → ghi warning comparability, không overclaim % |

## 5. API Baseline

| Metric | Baseline | Final | Change | Classification |
|---|---|---|---|---|
| startup | PENDING | PENDING | — | INCOMPARABLE |
| first prediction | PENDING | PENDING | — | INCOMPARABLE |
| warm p50 | PENDING | PENDING | — | INCOMPARABLE |
| warm p95 | PENDING | PENDING | — | INCOMPARABLE |
| max | PENDING | PENDING | — | INCOMPARABLE |
| failure rate | PENDING | PENDING | — | INCOMPARABLE |

*BLOCKED — không có live env. Không bịa số.*

## 6. Streamlit Baseline / Final

| Page | Baseline | Final | Change | Status |
|---|---|---|---|---|
| Home | PENDING | PENDING | — | INCOMPARABLE |
| Predict | PENDING | PENDING | — | INCOMPARABLE |
| Music Trends | PENDING | PENDING | — | INCOMPARABLE |
| Model Info | PENDING | PENDING | — | INCOMPARABLE |
| Explain | PENDING | PENDING | — | INCOMPARABLE |
| What-If | PENDING | PENDING | — | INCOMPARABLE |

## 7. Model Loading (Phase 2 Audit)

**ALREADY_OPTIMIZED.** Eager load tại lifespan + PipelineLoader singleton → **1 load/process, 0 reload/request**. Không có per-request deserialization. Thread/process semantics: load once PER PROCESS (đúng, không claim globally across workers). Source: `feature_3_6_model_loading_architecture.json`.

> Phase 2 là design audit — kết quả ALREADY_OPTIMIZED là thành công (không sửa code đã tối ưu), không phải gap.

## 8. Artifact Cache (Phase 2 Audit)

**ALREADY_OPTIMIZED.** PipelineLoader memoize schemas/metadata/features (1 lần/process). `model_metrics.json` đọc per /model-info → **NOT_JUSTIFIED** (file KB, không có live baseline chứng minh đáng kể). Registry: 9 artifacts. Source: `feature_3_6_artifact_cache_registry.json`.

## 9. Dashboard Cache (Phase 2 Audit)

**ALREADY_OPTIMIZED.** `@st.cache_data` 2 lớp (page path-keyed + F3.4 SHA-256-keyed); aggregation param-keyed. Dataset 169,681 rows không đọc lại khi warm.

## 10. Cache Correctness & Invalidation

Key contract + 4 invalidation cases + mutation safety (defensive copies) — contract valid từ source; live behavior BLOCKED. No-refit: 0 fit/fit_transform/partial_fit.

## 11. Performance Conclusion

**Không overclaim.** Không số đo nào tồn tại (BLOCKED).

**Lưu ý quan trọng về Phase 2:** Phase 2 (Tasks 3.6.3–3.6.5) là **evidence-driven design audit**, không phải implementation sprint. Mục tiêu là xác định có tồn tại cơ hội optimization hợp lý hay không. Kết quả:
- 4/5 candidate: **ALREADY_OPTIMIZED** — đã tối ưu từ trước (source evidence: PipelineLoader memoize, eager lifespan load, st.cache_data 2 lớp).
- 1/5 candidate: **NOT_JUSTIFIED** — không đủ dữ liệu baseline để chứng minh impact đáng kể.

**"Production code changed: 0" là kết quả đúng**, không phải thất bại. Nếu candidate đã tối ưu rồi thì không sửa thêm — đúng nguyên tắc engineering. Viết code vô ích chỉ để có diff mới là anti-pattern. Feature 3.6 Phase 2 **thành công** khi xác định đúng rằng hệ thống đã tối ưu, không cần thay đổi.

## 12. run_backend

Script tạo: artifact validation → port conflict (exit 2, **không kill**) → uvicorn chính xác → poll /health (model_loaded=true) → Ctrl+C cleanup (finally teardown, sửa orphan bug trong review) → propagate exit code. **Live smoke BLOCKED.**

## 13. run_frontend

Script tạo: port conflict (exit 2) → backend-unreachable **WARN** (không fail) → streamlit → /_stcore/health → cleanup. **Live smoke BLOCKED.**

## 14. run_all

Script tạo: validate → start backend → **poll /health thật (KHÔNG fixed sleep)** → start frontend → in URL → monitor → teardown chỉ con mình tạo (frontend trước, backend sau; graceful → terminate → kill). Backend chết trước ready → detect sớm (child.poll), không treo chờ timeout. **Live smoke BLOCKED.**

## 15. Port Handling

Occupied port → in thông báo + exit 2, **không kill process lạ**. Env override (`BACKEND_PORT`, `STREAMLIT_SERVER_PORT`) + giữ `BACKEND_BASE_URL` khớp.

## 16. Process Cleanup

PIDs tracked; teardown chỉ process do launcher tạo. Orphan: 0 (by design; live verify BLOCKED).

## 17. Backup Screenshots

Inventory 7 ảnh hoàn chỉnh (manifest + quality rules). **Đã capture: 0** — REQUIRES_LIVE_CAPTURE (không bịa). Dir: `demo/backup/screenshots/`.

## 18. Backup Demo Video

Status: **MANUAL_RECORDING_REQUIRED** — shot list 7 scenes (~3.5 min) + validation checklist sẵn sàng; chưa quay, không bịa file/metadata.

## 19. Offline Demo Mode

- Activation explicit (`OFFLINE_DEMO_MODE=true` hoặc UI offer khi connection/service-unavailable/timeout; **không bao giờ** trigger bởi 422).
- Banner nổi bật mọi page: "OFFLINE DEMO MODE — Precomputed validated result. No live model inference is being performed."
- Predict: chỉ canonical scenario (46, precomputed validated evidence); input khác bị reject.
- **Explain / What-If offline: NOT_AVAILABLE** — không có SHAP/delta đã validate; bịa = vi phạm honesty.
- Model Info: validated snapshot. Trends: tính từ dataset local (labeled local, không phải API snapshot).
- Live recovery: health probe → "Switch back to Live" → `demo_mode = LIVE`.

> **Offline results are precomputed validated evidence, not live inference.**

## 20. Demo Reliability Checklist

`demo_reliability_checklist.md` — 9 sections (Before Demo Day → Five Minutes Before Demo). Hoàn chỉnh.

## 21. Demo Runbook

`DEMO_RUNBOOK_FEATURE_3_6.md` — 18 sections: tested environment, ports, env vars, paths, start backend/frontend/all, normal flow, 9 failure-fallback procedures, offline mode, screenshots, video, return-to-live, shutdown. Traceability valid (env/port/command).

## 22. Full Tests

| Collected | Passed | Failed | Errors | Skipped |
|---|---|---|---|---|
| 0 | 0 | 0 | 0 | 0 |

**BLOCKED** (no live Python env). Spec 39 test files across phases + JUnit export `pytest_feature_3_6.xml` — chạy tại live acceptance.

## 23. Source Immutability

| Artifact | Modified |
|---|---|
| Model pipeline | NO |
| Schemas | NO |
| SHAP assets | NO |
| Trend dataset | NO |

## 24. Architecture Audit

frontend_direct_model_load=0 · frontend_dynamic_shap=0 · model_reload_per_request=0 · offline_fake_dynamic_inference=0 · hardcoded_prediction=0 · machine_specific_startup_path=0.

## 25. Warnings

1. **F36-W02** — Không có live baseline → BEFORE/AFTER vacuous. Đã được ghi nhận trong Mục 11.
2. **F36-W09** — Screenshots chưa capture (0/7 ảnh) — đánh dấu ⚠ INCOMPLETE trong bảng Task.
3. **F36-W10** — Demo video chưa record — đánh dấu ⚠ INCOMPLETE trong bảng Task.
4. **F36-W11** — Offline mode: design contract hoàn chỉnh nhưng **frontend UI chưa implement dòng code nào** — đánh dấu ⚠ CONTRACT_ONLY trong bảng Task. UI implementation + live smoke vẫn cần thực hiện khi có môi trường.

## 26. Blockers

1. **F36-B01** — Không có live Python environment → không thể: re-benchmark, smokes, pytest, capture media, live correctness guard.

## 27. Closure Gate

```
feature_3_6_status:   FAIL
feature_3_6_decision: NOT_CLOSED
feature_3_7_gate:     BLOCKED
human_approval:       PENDING
```

Lý do: toàn bộ FAIL đến từ F36-B01 (điều kiện môi trường), **không phải lỗi implementation**. Mọi artifact design/evidence/documentation đều hoàn chỉnh và trung thực. Closure cần một live acceptance run.

## 28. Feature 3.7 Readiness

**BLOCKED.** Cần: 3.6 PASS/PASS_WITH_WARNINGS, benchmark complete, 0 correctness regression, run_* smokes pass, pytest 0 fail/error, source unchanged, blockers rỗng.

## 29. Kết luận

Feature 3.6 đã hoàn thành toàn bộ phần thiết kế + deliverable có thể tạo offline (scripts, contracts, evidence registry, checklist, runbook, manifest, gate, reports) — **trung thực, không bịa media/số liệu**. Chưa đủ điều kiện nghiệm thu vì phần acceptance live chưa chạy được. Khi có môi trường Python: chạy `python scripts/run_all.py` + benchmark + pytest + capture + smokes theo runbook, cập nhật 4 marker BLOCKED, chạy lại closure logic.

| Task | Công việc | Evidence | Status |
|---|---|---|---|
| 3.6.1 | API benchmark | feature_3_6_api_latency_baseline/final | BLOCKED |
| 3.6.2 | Streamlit benchmark | feature_3_6_streamlit_page_latency_baseline/final | BLOCKED |
| 3.6.3 | Model loading (audit) | feature_3_6_model_loading_architecture.json | ✅ Audit → ALREADY_OPTIMIZED |
| 3.6.4 | Artifact cache (audit) | feature_3_6_artifact_cache_registry.json | ✅ Audit → ALREADY_OPTIMIZED |
| 3.6.5 | Dashboard cache (audit) | feature_3_6_dashboard_cache_key_contract.json | ✅ Audit → ALREADY_OPTIMIZED |
| 3.6.6 | run_backend | scripts/run_backend.py | ✅ created (live BLOCKED) |
| 3.6.7 | run_frontend | scripts/run_frontend.py | ✅ created (live BLOCKED) |
| 3.6.8 | run_all | scripts/run_all.py | ✅ created (live BLOCKED) |
| 3.6.9 | Screenshots | feature_3_6_backup_screenshot_manifest.json | ⚠ INCOMPLETE (0 captured) |
| 3.6.10 | Demo video | feature_3_6_demo_video_shot_list.md | ⚠ INCOMPLETE (MANUAL_RECORDING_REQUIRED) |
| 3.6.11 | Offline mode (design) | feature_3_6_offline_demo_mode_contract.json | ⚠ CONTRACT_ONLY (frontend NOT implemented) |
| 3.6.12 | Reliability checklist | demo_reliability_checklist.md | ✅ |
| 3.6.13 | Runbook/config/fallback | DEMO_RUNBOOK_FEATURE_3_6.md | ✅ |
| Final | Re-benchmark + smokes + tests | feature_3_6_final_validation_results.json | BLOCKED (F36-B01) |

**Reviewer:** Chưa chỉ định
**Human approval:** PENDING

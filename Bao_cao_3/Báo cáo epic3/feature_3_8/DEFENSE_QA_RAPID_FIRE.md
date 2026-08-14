# Defense Q&A — Rapid Fire

1. **Dataset bao nhiêu dòng?** → Locked ML pipeline và story/slide hiện dùng 586.672 dòng, 1900–2021; một số legacy docs còn số cũ và không phải nguồn canonical.
2. **Bao nhiêu input?** → API nhận 18 raw fields; feature engineering thành 31 selected và preprocessing thành 49 model columns.
3. **Target là gì?** → Spotify popularity 0–100, một historical platform proxy, không phải hit probability.
4. **Split ra sao?** → Temporal: train 1900–2004, validation 2005–2013, test 2014–2021.
5. **Vì sao temporal?** → Để tránh trộn tương lai vào quá khứ và nhìn thấy temporal shift thực tế hơn random split.
6. **Có missing không?** → Có: release_month 136.489, tempo 328, time_signature 337 trong ML-ready evidence; xử lý train-only.
7. **Có leakage không?** → Các guardrail target/proxy, train-only fit và split-overlap đều pass; không tuyên bố mọi dạng leakage tuyệt đối bằng 0.
8. **Model gì?** → XGBoost regression `EXP24-XGB-FINAL-001`, model version 1.0.0.
9. **Vì sao XGBoost?** → CV/validation tốt nhất ghi nhận, nhỉnh hơn Random Forest và fit nhanh hơn trong run artifact.
10. **Đã thử model nào?** → XGBoost, Random Forest, Ridge; registry có Dummy và Linear baselines.
11. **MAE?** → 17.65 popularity points trên 85.876 test rows.
12. **RMSE?** → 21.01; phạt large errors mạnh hơn MAE.
13. **R²?** → 0.0696, khoảng 7% variance trong setup; không phải accuracy.
14. **Model có overfit không?** → Không thể khẳng định không; train/validation/test RMSE là 11.279/15.252/21.013.
15. **Validation sang test?** → RMSE tăng 37.77%, artifact ghi `LARGE_DEGRADATION`.
16. **Tại sao không deep learning?** → Không có evaluated DL run trong project; không đưa comparative claim.
17. **Prediction có chắc hit không?** → Không; model estimate với measured error và limited target.
18. **SHAP là gì?** → Attribution cho contribution vào model prediction, không phải causal explanation.
19. **Explainer nào?** → TreeExplainer, background train-only 1.000×49.
20. **Additivity?** → 5.000/5.000 rows pass tolerance 0.001; đó là numerical reconstruction, không phải causal proof.
21. **SHAP tính ở đâu?** → FastAPI backend; Streamlit chỉ render.
22. **What-if causal không?** → Không; nó chạy lại cùng model với input sửa và so hai outputs.
23. **Production-ready chưa?** → Chưa; đây là local academic prototype, không có production hardening/SLA.
24. **API chết thì sao?** → Check/retry một lần rồi disclosed OFFLINE_PRECOMPUTED; Explain/What-if NOT_AVAILABLE.
25. **Cải thiện gì trước?** → Reconcile nốt legacy docs, đo Explain lặp lại thay vì dựa một smoke, thêm recent/context data an toàn, đánh giá drift rồi harden deployment.

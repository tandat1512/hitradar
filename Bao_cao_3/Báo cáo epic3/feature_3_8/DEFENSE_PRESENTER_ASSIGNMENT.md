# Defense Presenter Assignment — Human Confirmation Required

**Assignment status:** `TEMPLATE_READY_HUMAN_CONFIRMATION_REQUIRED`  
**PRIMARY_DEMO_OPERATOR:** `UNASSIGNED`  
**BACKUP_DEMO_OPERATOR:** `UNASSIGNED`

Project documents verify contributors Minh and Đạt, but do not prove an agreed defense roster or consent to these roles. Therefore this table is a sign-off template, not an actual assignment.

| Section | Primary presenter | Backup presenter | Demo role | Q&A specialty | Handoff note |
|---|---|---|---|---|---|
| Introduction / problem | UNASSIGNED | UNASSIGNED | None | Project scope basics | Hand off to Dataset |
| Dataset / preprocessing | UNASSIGNED | UNASSIGNED | Trends support | Dataset, split, leakage | Hand off to Model |
| Model / metrics | UNASSIGNED | UNASSIGNED | Predict support | Model selection, metrics | Hand off to SHAP |
| SHAP / What-if | UNASSIGNED | UNASSIGNED | Explain/What-if support | SHAP, noncausal wording | Hand off to Architecture |
| Architecture / productization | UNASSIGNED | UNASSIGNED | API health support | FastAPI, Streamlit, serving | Hand off to Live Demo |
| Live demo operator | UNASSIGNED | UNASSIGNED | PRIMARY_DEMO_OPERATOR | UI/demo recovery | Hand off to Limitations |
| Limitations / responsible use | UNASSIGNED | UNASSIGNED | Fallback disclosure support | Data/model/operational limits | Hand off to Conclusion |
| Conclusion | UNASSIGNED | UNASSIGNED | None | Top-level recap | Open Q&A |

## Q&A ownership sign-off

| Category | Primary lead | Backup lead | All members know basics | Human confirmed |
|---|---|---|---|---|
| Dataset questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |
| Model questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |
| SHAP / What-if questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |
| System / API questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |
| UI / demo questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |
| Limitations questions | UNASSIGNED | UNASSIGNED | REQUIRED | NO |

## Demo operator checklist before sign-off

The actual primary and backup operator must both demonstrate:

- `python scripts/run_all.py` and ports 8000/8501;
- health checks and `model_loaded=true`;
- canonical input and live/offline distinction;
- exact offline disclosure;
- Explain timeout skip rule;
- current backup status: screenshots missing, video `MANUAL_RECORDING_REQUIRED`.

## Human sign-off

- Confirmed roster/date: `PENDING`
- Primary demo operator acceptance: `PENDING`
- Backup demo operator acceptance: `PENDING`
- Section/Q&A owner acceptance: `PENDING`

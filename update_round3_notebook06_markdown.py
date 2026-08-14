"""Apply Round-3 wording corrections to Notebook 06 without retraining it."""

from pathlib import Path

import nbformat


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "3.NOTEBOOKS" / "3.6.modeling" / "06_machine_learning.ipynb"
notebook = nbformat.read(PATH, as_version=4)

replacements = {
    "Protocol: **Selection Train (`release_year <= 2017`) → Validation (`2018`) → lock configuration → refit from scratch on Development (`<2019`) → Final Test (`>=2019`) exactly once**. Final-test performance cannot change the locked winner.": (
        "Protocol: **Selection Train (`release_year <= 2017`) → Validation (`2018`) → lock configuration → refit from scratch on Development (`<2019`) → Final Test (`>=2019`) exactly once**. Final-test performance cannot change the locked winner. Trong lần chạy Round 2 đã hiệu chỉnh, 2019+ không được dùng để chọn winner; tuy nhiên chính giai đoạn này đã được xem trong một vòng phát triển trước, nên không được hiểu là test set chưa từng được quan sát trong toàn bộ lịch sử dự án."
    ),
    "The final-test labels are not loaded into a model-selection variable. Before lock, only its row count is shown; its target summary and metrics are computed after the winner-lock artifact exists.": (
        "Trong lần chạy Round 2 đã hiệu chỉnh, labels 2019+ không được nạp vào biến chọn mô hình; trước khi lock chỉ hiển thị số dòng. Đây là phạm vi của bằng chứng lock trong Round 2, không phải khẳng định rằng giai đoạn 2019+ chưa từng được kiểm tra trong lịch sử dự án."
    ),
    "The selection table contains validation evidence only. The final pipeline configuration equals the persisted lock, was refit on all pre-2019 development data, and was evaluated once on the 2019+ final horizon. Modest or worse final performance is reported without changing the winner.": (
        "The selection table contains validation-2018 evidence only. The final pipeline configuration equals the persisted lock, was refit on all pre-2019 development data, and then evaluated on the 2019+ horizon without changing the winner. The corrected Round-2 pipeline did not use that horizon for winner selection; however, the same horizon had been inspected during an earlier development iteration, so it is not a historically never-observed test set."
    ),
}

changed = 0
for cell in notebook.cells:
    if cell.cell_type != "markdown":
        continue
    for old, new in replacements.items():
        if old in cell.source:
            cell.source = cell.source.replace(old, new)
            changed += 1

if changed != len(replacements):
    raise AssertionError(f"Expected {len(replacements)} markdown replacements, got {changed}")
nbformat.write(notebook, PATH)
print(f"Updated {changed} Notebook 06 markdown cells without executing model code: {PATH}")

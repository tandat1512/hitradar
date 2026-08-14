@echo off
REM Feature 3.7 Bugfix Cleanup — BUG 1
REM Deletes the duplicate Phase 2 report stub
del "H:\dự án\DUAN1 github\Bao_cao_3\Báo cáo epic3\feature_3_7\FEATURE_3_7_USER_DOCUMENTATION_REPORT.md"
if exist "H:\dự án\DUAN1 github\Bao_cao_3\Báo cáo epic3\feature_3_7\FEATURE_3_7_USER_DOCUMENTATION_REPORT.md" (
    echo FAILED: file still exists
) else (
    echo DELETED: FEATURE_3_7_USER_DOCUMENTATION_REPORT.md
)
pause

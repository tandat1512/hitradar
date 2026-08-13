import os, sys
target = r"H:\dự án\DUAN1 github\Bao_cao_3\Báo cáo epic3\feature_3_7\FEATURE_3_7_USER_DOCUMENTATION_REPORT.md"
if os.path.exists(target):
    os.remove(target)
    print(f"DELETED: {target}")
else:
    print(f"NOT FOUND: {target}")

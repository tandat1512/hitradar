import os, sys
target = r"<PROJECT_ROOT>"
if os.path.exists(target):
    os.remove(target)
    print(f"DELETED: {target}")
else:
    print(f"NOT FOUND: {target}")

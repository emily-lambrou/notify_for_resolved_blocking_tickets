import re

def extract_related_issues(body):
    if not body:
        return []
    return list(set(re.findall(r"#(\d+)", body)))

def extract_related_issues(body):
    if not body:
        return []

    pattern = r"(?:[\w\-.]+\/[\w\-.]+#\d+|[\w\-.]+#\d+|#\d+|https?://[^/]+/[\w\-.]+/[\w\-.]+/issues/\d+)"
    
    matches = re.findall(pattern, body)

    return list(dict.fromkeys(matches))

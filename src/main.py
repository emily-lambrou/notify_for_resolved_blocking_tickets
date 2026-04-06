import os
import json
from config import DRY_RUN
from graphql import get_issue_by_number, add_comment
from utils import extract_related_issues

def main():
    event_path = os.environ["GITHUB_EVENT_PATH"]

    with open(event_path) as f:
        event = json.load(f)

    issue_data = event.get("issue")
    if not issue_data:
        return

    issue_number = issue_data["number"]
    issue_state = issue_data["state"]

    # Only run when issue is closed
    if issue_state != "closed":
        return

    issue = get_issue_by_number(issue_number)
    labels = [l["name"].lower() for l in issue["labels"]["nodes"]]

    # Only proceed if closed issue has label "blocking"
    if "blocking" not in labels:
        return

    related_numbers = extract_related_issues(issue.get("body", ""))

    for num in related_numbers:
        related_issue = get_issue_by_number(int(num))

        if related_issue["state"] != "OPEN":
            continue

        related_labels = [l["name"].lower() for l in related_issue["labels"]["nodes"]]

        if "blocked" in related_labels:
            message = f"Ticket #{issue_number} has been resolved. Please check if this unblocked the current one"

            if not DRY_RUN:
                add_comment(related_issue["id"], message)

if __name__ == "__main__":
    main()

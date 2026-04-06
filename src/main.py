import os
import json
from config import DRY_RUN
from graphql import (
    get_issue_by_number,
    get_project_status,
    add_comment,
)
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

    # Run only when issue is closed
    if issue_state != "closed":
        return

    # Fetch full issue details
    issue = get_issue_by_number(issue_number)

    labels = [
        label["name"].lower()
        for label in issue["labels"]["nodes"]
    ]

    # Continue only if closed issue has label "blocking"
    if "blocking" not in labels:
        return

    # Extract related issue numbers from body
    related_numbers = extract_related_issues(
        issue.get("body", "")
    )

    for num in related_numbers:
        related_issue = get_issue_by_number(int(num))

        # Only process OPEN issues
        if related_issue["state"] != "OPEN":
            continue

        related_labels = [
            label["name"].lower()
            for label in related_issue["labels"]["nodes"]
        ]

        project_status = get_project_status(
            related_issue["id"]
        )

        is_blocked_label = "blocked" in related_labels
        is_blocked_status = (
            project_status is not None
            and project_status.lower() == "blocked"
        )

        # Comment if label OR project status is Blocked
        if is_blocked_label or is_blocked_status:

            message = (
                f"Ticket #{issue_number} has been resolved. "
                f"Please check if this unblocked the current one."
            )

            if DRY_RUN:
                print(
                    f"[DRY RUN] Would comment on issue #{num}"
                )
            else:
                add_comment(
                    related_issue["id"],
                    message
                )


if __name__ == "__main__":
    main()

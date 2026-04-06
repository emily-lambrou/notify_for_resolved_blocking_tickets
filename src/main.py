from logger import logger
import config
import graphql
from utils import extract_related_issues
import os


def notify_closed_blocking_issue(issue_number):
    logger.info(f"Processing closed issue #{issue_number}")

    issue = graphql.get_issue_by_number(int(issue_number))

    labels = [
        label["name"].lower()
        for label in issue["labels"]["nodes"]
    ]

    # Only proceed if issue has label "blocking"
    if "blocking" not in labels:
        logger.info("Issue is not labeled 'blocking'. Skipping.")
        return

    related_refs = extract_related_issues(
        issue.get("body", "")
    )

    if not related_refs:
        logger.info("No related issues found.")
        return

    for ref in related_refs:
        related_issue = graphql.resolve_issue_reference(ref)

        if not related_issue:
            continue

        if related_issue["state"] != "OPEN":
            continue

        related_labels = [
            label["name"].lower()
            for label in related_issue["labels"]["nodes"]
        ]

        project_status = graphql.get_issue_status(
            related_issue["id"],
            config.status_field_name
        )

        is_blocked_label = "blocked" in related_labels
        is_blocked_status = (
            project_status is not None
            and project_status.lower() == "blocked"
        )

        if is_blocked_label or is_blocked_status:
            message = (
                f"Ticket #{issue_number} has been resolved. "
                f"Please check if this unblocked the current one."
            )

            if config.DRY_RUN:
                logger.info(
                    f"[DRY RUN] Would comment on issue #{related_issue['number']}"
                )
            else:
                graphql.add_issue_comment(
                    related_issue["id"],
                    message
                )
                logger.info(
                    f"✅ Comment added to issue #{related_issue['number']}"
                )


def main():
    logger.info("🔄 Blocking resolution process started...")

    issue_number = os.getenv("INPUT_ISSUE_NUMBER")

    if not issue_number:
        logger.error("No issue number provided.")
        return

    notify_closed_blocking_issue(issue_number)


if __name__ == "__main__":
    main()

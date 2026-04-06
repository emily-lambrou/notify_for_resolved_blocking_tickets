from logger import logger
import config
import graphql
from utils import extract_related_issues


def notify_closed_blocking_issues():
    logger.info("Fetching recently closed issues...")

    closed_issues = graphql.get_recent_closed_issues(
        owner=config.repository_owner,
        repo=config.repository_name
    )

    if not closed_issues:
        logger.info("No recently closed issues found.")
        return

    for issue in closed_issues:
        issue_id = issue["id"]
        issue_number = issue["number"]

        labels = [
            label["name"].lower()
            for label in issue["labels"]["nodes"]
        ]

        # Only process issues labeled "blocking"
        if "blocking" not in labels:
            continue

        logger.info(f"Processing closed blocking issue #{issue_number}")

        related_refs = extract_related_issues(
            issue.get("body", "")
        )

        if not related_refs:
            logger.info(
                f"Issue #{issue_number} has no related issues."
            )
            continue

        for ref in related_refs:
            related_issue = graphql.resolve_issue_reference(ref)

            if not related_issue:
                logger.warning(
                    f"Could not resolve issue reference '{ref}'."
                )
                continue

            related_issue_id = related_issue["id"]
            related_issue_number = related_issue["number"]
            related_issue_state = related_issue.get("state")

            # Only process OPEN issues
            if related_issue_state != "OPEN":
                continue

            related_labels = [
                label["name"].lower()
                for label in related_issue["labels"]["nodes"]
            ]

            project_status = graphql.get_issue_status(
                related_issue_id,
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

                if config.dry_run:
                    logger.info(
                        f"[DRY RUN] Would comment on issue #{related_issue_number}"
                    )
                else:
                    graphql.add_issue_comment(
                        related_issue_id,
                        message
                    )
                    logger.info(
                        f"✅ Comment added to issue #{related_issue_number}"
                    )


def main():
    logger.info("🔄 Blocking resolution process started...")

    if config.dry_run:
        logger.info("DRY RUN MODE ON!")

    notify_closed_blocking_issues()


if __name__ == "__main__":
    main()

# notify_for_resolved_blocking_tickets
Every time a blocking ticket is resolved, find the blocked issues and notify the stakeholders


## Introduction

This GitHub Action triggers when a blocking issue is resolved (closed) and then it pulls all the related issues in the description/body of this ticket. 
Then, it notifies the stakeholders in all the related issues (only if the label "blocked" or status "Blocked" is present) that the ticket XXX has been resolved in order to check if they can proceed.

### Prerequisites

Before you can start using this GitHub Action, you'll need to ensure you have the following:

1. A GitHub repository where you want to enable this action.
2. A GitHub project board.
3. "Status" field should be "Single select" type and has a value "Blocked"
4. "blocked" and "blocking" value as labels.
5. A Token (Classic) with permissions to repo:*, read:user, user:email, read:project

### Inputs

| Input                                | Description                                                                                      |
|--------------------------------------|--------------------------------------------------------------------------------------------------|
| `gh_token`                           | The GitHub Token                                                                                 |
| `project_number`                     | The project number                                                                               |                                                         
| `enterprise_github` _(optional)_     | `True` if you are using enterprise github and false if not. Default is `False`                   |
| `repository_owner_type` _(optional)_ | The type of the repository owner (oragnization or user). Default is `user`                       |
| `dry_run` _(optional)_               | `True` if you want to enable dry-run mode. Default is `False`                                    |


### Examples

#### Notify for close blocking issues with comment
To set up blocking issues comment notifications, you'll need to create or update a GitHub Actions workflow in your repository. Below is
an example of a workflow YAML file:

```yaml
name: Notify stakeholders if a blocking issue is resolved

on:
  issues:
    types: [closed]

concurrency:
  group: notify_blocked_issues
  cancel-in-progress: true

jobs:
  notify_blocked_issues:
    runs-on: self-hosted
    timeout-minutes: 10

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v3

      - name: Notify Blocked Issues When Blocking Issues Has Been Resolved
        uses: emily-lambrou/notify_for_resolved_blocking_tickets@v1.0
        with:
          gh_token: ${{ secrets.GH_TOKEN }}
          project_number: ${{ vars.PROJECT_NUMBER }}
          dry_run: ${{ vars.DRY_RUN }}
          enterprise_github: 'True' 
          repository_owner_type: organization"
        
```


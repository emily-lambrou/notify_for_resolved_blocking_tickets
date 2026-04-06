import requests
import re
from config import GRAPHQL_URL, HEADERS, OWNER, REPO_NAME, PROJECT_NUMBER


def run_query(query, variables=None):
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()


# -------------------------------------------------------------------
# Get issue by number (same repository)
# -------------------------------------------------------------------
def get_issue_by_number(number):
    query = '''
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
          number
          state
          labels(first: 20) { nodes { name } }
          body
        }
      }
    }
    '''
    data = run_query(query, {
        "owner": OWNER,
        "repo": REPO_NAME,
        "number": number
    })
    return data["data"]["repository"]["issue"]


# -------------------------------------------------------------------
# Resolve issue reference (supports cross-repo references)
# -------------------------------------------------------------------
def resolve_issue_reference(reference):
    """
    Supports:
      - #123
      - repo#123
      - org/repo#123
    """

    match = re.match(
        r"(?:(?P<org>[\w\-.]+)/(?P<repo>[\w\-.]+))?#(?P<number>\d+)",
        reference,
    )

    if not match:
        return None

    owner = match.group("org") or OWNER
    repo = match.group("repo") or REPO_NAME
    number = int(match.group("number"))

    query = '''
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $number) {
          id
          number
          state
          labels(first: 20) { nodes { name } }
          body
        }
      }
    }
    '''

    data = run_query(query, {
        "owner": owner,
        "repo": repo,
        "number": number
    })

    repo_data = data.get("data", {}).get("repository")

    if not repo_data:
        return None

    return repo_data.get("issue")


# -------------------------------------------------------------------
# Get project status
# -------------------------------------------------------------------
def get_project_status(issue_id):
    query = '''
    query($owner: String!, $projectNumber: Int!) {
      organization(login: $owner) {
        projectV2(number: $projectNumber) {
          items(first: 100) {
            nodes {
              content {
                ... on Issue {
                  id
                }
              }
              fieldValueByName(name: "Status") {
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                }
              }
            }
          }
        }
      }
    }
    '''

    data = run_query(query, {
        "owner": OWNER,
        "projectNumber": PROJECT_NUMBER
    })

    items = data["data"]["organization"]["projectV2"]["items"]["nodes"]

    for item in items:
        content = item.get("content")
        if content and content.get("id") == issue_id:
            status = item.get("fieldValueByName")
            if status:
                return status["name"]

    return None


# -------------------------------------------------------------------
# Add comment
# -------------------------------------------------------------------
def add_comment(issue_id, body):
    mutation = '''
    mutation($subjectId: ID!, $body: String!) {
      addComment(input: {subjectId: $subjectId, body: $body}) {
        clientMutationId
      }
    }
    '''
    run_query(mutation, {"subjectId": issue_id, "body": body})

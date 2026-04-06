import requests
from config import GRAPHQL_URL, HEADERS, OWNER, REPO_NAME

def run_query(query, variables=None):
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables or {}},
        headers=HEADERS,
    )
    response.raise_for_status()
    return response.json()

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

def add_comment(issue_id, body):
    mutation = '''
    mutation($subjectId: ID!, $body: String!) {
      addComment(input: {subjectId: $subjectId, body: $body}) {
        clientMutationId
      }
    }
    '''
    run_query(mutation, {"subjectId": issue_id, "body": body})

import requests
import os
import base64

def list_org_repos(org, token):
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/orgs/{org}/repos?type=all&per_page=100&page={page}"
        headers = {"Authorization": f"token {token}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            batch = response.json()
            if not batch:
                break
            repos.extend([repo['full_name'] for repo in batch])
            page += 1
        else:
            raise Exception(f"Failed to fetch repositories: {response.content}")
    return repos

def get_workflow_files(repo, token):
    url = f"https://api.github.com/repos/{repo}/contents/.github/workflows"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch workflow files from {repo}: {response.content}")

def get_file_content(repo, path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return base64.b64decode(response.json()['content']).decode('utf-8')
    else:
        raise Exception(f"Failed to fetch file content from {repo}: {response.content}")

def update_workflow_in_repo(repo, path, content, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    data = {
        "message": f"Update workflow file {path}",
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "sha": get_existing_file_sha(repo, path, token)  # Get the SHA if the file exists
    }
    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        raise Exception(f"Failed to update file in {repo}: {response.content}")

def get_existing_file_sha(repo, path, token):
    url = f"https://api.github.com/repos/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['sha']
    return None

def github_directory_exists(repo, token):
    url = f"https://api.github.com/repos/{repo}/contents/.github"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200
def main():
    token = os.getenv("GITHUB_TOKEN")
    org_name = "GuineaBot3Labs"  # Replace with your organization name
    source_repo = "GuineaBot3Labs/.github"  # Replace with your source repository

    target_repos = list_org_repos(org_name, token)
    workflow_files = get_workflow_files(source_repo, token)

    for repo in target_repos:
        if repo != source_repo and not github_directory_exists(repo, token):  
            # Only proceed if .github doesn't exist in the target repository
            for file_info in workflow_files:
                content = get_file_content(source_repo, file_info['path'], token)
                update_workflow_in_repo(repo, file_info['path'], content, token)
                print(f"Updated {file_info['path']} in {repo}")                
if __name__ == "__main__":
    main()

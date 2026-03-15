import os
import subprocess
import requests
import logging
import re
import shutil

# =========================
# CONFIG
# =========================
GITHUB_USER   = "<YOUR-USERNAME>"
GITHUB_TOKEN  = "<YOUR-GITHUB-TOKEN>" 
GITLAB_TOKEN  = "<YOUR-GITLAB-TOKEN>"

# Grupas ID
PUBLIC_GROUP_ID  = 116797979
PRIVATE_GROUP_ID = 116798188

CACHE_DIR = "/home/python/git_cache"

# Not required
NOTIFY_URL  = "https://your-netfy-server.com"
NOTIFY_USER = "NTFY-Token"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def notify(msg):
    try:
        subprocess.run([
            "curl", "-u", f":{NOTIFY_USER}", 
            "-d", msg, NOTIFY_URL
        ], capture_output=True)
    except Exception as e:
        logging.error(f"Couldn t send message: {e}")

# =========================
# GITHUB: 
# =========================
def get_github_repos():
    # Pārliecinies, ka šeit ir 'token ' (ar atstarpi) un tad mainīgais
    headers = {"Authorization": f"token {GITHUB_TOKEN.strip()}"} 

    
    logging.info(f"DEBUG HEADERS: {headers}") 

    repos = []    
    def fetch_paged(url_base):
        results = []
        page = 1
        while True:
            r = requests.get(f"{url_base}&page={page}", headers=headers)
            if r.status_code != 200:
                notify(f" GitHub API kļūda: {r.text}")
                break
            data = r.json()
            if not data:
                break
            results.extend(data)
            page += 1
        return results

    # Personal
    repos.extend(fetch_paged("https://api.github.com/user/repos?per_page=100&type=all"))
    
    # Organization
    repos.extend(fetch_paged("https://api.github.com/orgs/hugovalters/repos?per_page=100"))

    return repos

# =========================
# GITLAB: pārbauda/izveido projektu
# =========================
def safe_slug(name):
    slug = name.lower()
    slug = re.sub(r"[^a-z0-9._-]", "-", slug)
    slug = slug.strip("._-")
    return slug or "repo"

def create_or_get_gitlab_project(repo_name, visibility, namespace_id):
    url = "https://gitlab.com/api/v4/projects"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    
    search_slug = safe_slug(repo_name)
    search_url = f"https://gitlab.com/api/v4/projects?search={search_slug}&simple=true"
    
    try:
        r_search = requests.get(search_url, headers=headers)
        if r_search.status_code == 200:
            for proj in r_search.json():
                # Pārbaudām, vai vārds sakrīt un vai atrodas pareizajā grupā (Namespace)
                if proj["name"] == repo_name and proj["namespace"]["id"] == namespace_id:
                    return proj["http_url_to_repo"]
    except Exception as e:
        logging.error(f"Kļūda meklējot projektu GitLab: {e}")

    # Ja nav atrasts, veidojam jaunu
    data = {
        "name": repo_name,
        "path": search_slug,
        "namespace_id": namespace_id,
        "visibility": "public" if visibility == "public" else "private"
    }

    r = requests.post(url, headers=headers, data=data)
    if r.status_code == 201:
        logging.info(f" Created Github repo: {repo_name}")
        return r.json()["http_url_to_repo"]
    elif r.status_code == 400 and "has already been taken" in r.text:
        return create_or_get_gitlab_project(repo_name, visibility, namespace_id) 
    else:
        notify(f"GitLab create error {repo_name}: {r.text}")
        return None

# =========================
# GIT: Optimizēta sinhronizācija (Persistent Cache)
# =========================
def sync_repo(repo_name, github_url, gitlab_url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    repo_dir = os.path.join(CACHE_DIR, f"{safe_slug(repo_name)}.git")
    
    # Sagatavojam URL ar autentifikāciju
    github_auth = github_url.replace("https://github.com/", f"@github.com/">https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/")
    gitlab_auth = gitlab_url.replace("https://gitlab.com/", f"@gitlab.com/">https://oauth2:{GITLAB_TOKEN}@gitlab.com/")

    try:
        if not os.path.exists(repo_dir):
            logging.info(f"Clone new: {repo_name}...")
            subprocess.run(
                ["git", "clone", "--mirror", github_auth, repo_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            subprocess.run(
                ["git", "remote", "set-url", "--push", "origin", gitlab_auth],
                cwd=repo_dir, check=True
            )
        else:
            subprocess.run(["git", "remote", "set-url", "origin", github_auth], cwd=repo_dir, check=True)
            subprocess.run(["git", "remote", "set-url", "--push", "origin", gitlab_auth], cwd=repo_dir, check=True)
            
            logging.info(f"zzz Pārbaudām izmaiņas: {repo_name}...")
            subprocess.run(
                ["git", "remote", "update"],
                cwd=repo_dir,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )

        # 2. SOLIS: Spiežam uz GitLab (Push)
        result = subprocess.run(
            ["git", "push", "--mirror"],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            if "Everything up-to-date" in result.stderr:
                pass 
            else:
                logging.info(f" Sent changes to github: {repo_name}")
        else:
            notify(f" Push error {repo_name}: {result.stderr}")

    except subprocess.CalledProcessError as e:
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)
        notify(f" Sync error {repo_name}: {e}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    logging.info("--- Sākam sinhronizāciju ---")
    repos = get_github_repos()
    
    count = 0
    for repo in repos:
        name = repo["name"]
        visibility = repo["visibility"]
        clone_url = repo["clone_url"]

        namespace = PUBLIC_GROUP_ID if visibility == "public" else PRIVATE_GROUP_ID

        gitlab_repo_url = create_or_get_gitlab_project(name, visibility, namespace)
        if gitlab_repo_url:
            sync_repo(name, clone_url, gitlab_repo_url)
            count += 1
            
    logging.info(f"--- Beigta sinhronizācija (Apstrādāti: {count}) ---")

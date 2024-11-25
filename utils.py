import requests
import datetime
import subprocess
import glob
import time
import os
import json
import hashlib


GEOLOCATION_DEV = "GEOLOCATION-0A41430434C388A9"
GEOLOCATION_SPRINT = "GEOLOCATION-3F7C50D0C9065578"
GEOLOCATION_LIVE = "GEOLOCATION-45AB48D9D6925ECC"

# Set environment information
SSO_TOKEN_URL_DEV = "https://sso-dev.dynatracelabs.com/sso/oauth2/token"
SSO_TOKEN_URL_SPRINT = "https://sso-sprint.dynatracelabs.com/sso/oauth2/token"
SSO_TOKEN_URL_LIVE = "https://sso.dynatrace.com/sso/oauth2/token"
DT_RW_API_TOKEN = os.environ.get("DT_RW_API_TOKEN") # token to create all other tokens
DT_ENV_NAME = os.environ.get("DT_ENV_NAME") # abc12345
DT_ENV = os.environ.get("DT_ENV", "live") # dev, sprint" or "live"

SENSITIVE_WORDS = ["secret", "secrets", "token", "tokens", "generate-token"]

BACKSTAGE_PORT_NUMBER = 30105
ARGOCD_PORT_NUMBER = 30100
DEMO_APP_PORT_NUMBER = 80

BACKSTAGE_PORT_NUMBER = 30105
ARGOCD_PORT_NUMBER = 30100
DEMO_APP_PORT_NUMBER = 80

STANDARD_TIMEOUT="300s"
WAIT_FOR_ARTIFACT_TIMEOUT = 60
WAIT_FOR_ACCOUNTS_TIMEOUT = 60

COLLECTOR_WAIT_TIMEOUT_SECONDS = 30
OPENTELEMETRY_COLLECTOR_ENDPOINT = "http://localhost:4318"
CODESPACE_NAME = os.environ.get("CODESPACE_NAME")

GITHUB_ORG_SLASH_REPOSITORY = os.environ.get("GITHUB_REPOSITORY") # eg. yourOrg/yourRepo
GITHUB_REPO_NAME = os.environ.get("RepositoryName") # eg. mclass
GITHUB_DOT_COM_REPO = f"https://github.com/{GITHUB_ORG_SLASH_REPOSITORY}.git"
GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN = os.environ.get("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
DT_OAUTH_CLIENT_ID = os.environ.get("DT_OAUTH_CLIENT_ID")
DT_OAUTH_CLIENT_SECRET = os.environ.get("DT_OAUTH_CLIENT_SECRET")
DT_OAUTH_ACCOUNT_URN = os.environ.get("DT_OAUTH_ACCOUNT_URN")

def run_command(args, ignore_errors=False):
    output = subprocess.run(args, capture_output=True, text=True)

    set1 = set(args)
    set2 = set(SENSITIVE_WORDS)
    common_elems = (set1 & set2)
    if not common_elems:
        print(output.stdout)

    # Annoyingly, if git has nothing to commit
    # it exits with a returncode == 1
    # So ignore any git errors but exit for all others
    if not ignore_errors and output.returncode > 0:
        exit(f"Got an error! Return Code: {output.returncode}. Error: {output.stderr}. Stdout: {output.stdout}. Exiting.")
    return output

def do_file_replace(pattern="", find_string="", replace_string="", recursive=False):
    for filepath in glob.iglob(pattern, recursive=recursive):
        TARGET_FILE = False
        with open(filepath, "r") as file: # open file in read mode only first
            file_content = file.read()
            if find_string in file_content:
                TARGET_FILE = True
        # Replace the text
        file_content = file_content.replace(find_string, replace_string)

        if TARGET_FILE:
            with open(filepath, "w") as file: # now open in write mode and write
                file.write(file_content)

def git_commit(target_file="", commit_msg="", push=False):
    output = run_command(["git", "add", target_file], ignore_errors=True)
    output = run_command(["git", "commit", "-m", commit_msg], ignore_errors=True)
    if push:
        output = run_command(["git", "push"], ignore_errors=True)

# Whereas the kubectl wait command can be used to wait for EXISTING artifacts (eg. deployments) to be READY.
# kubectl wait will error if the artifact DOES NOT EXIST YET.
# This function first waits for it to even exist
# eg. wait_for_artifact_to_exist(namespace="default", artifact_type="deployment", artifact_name="backstage")
def wait_for_artifact_to_exist(namespace="default", artifact_type="", artifact_name=""):
    count = 1
    get_output = run_command(["kubectl", "-n", namespace, "get", f"{artifact_type}/{artifact_name}"], ignore_errors=True)

    # if artifact does not exist, important output will be in stderr
    # if artifact DOES exist, use stdout
    if get_output.stderr != "":
        get_output = get_output.stderr
    else:
        get_output = get_output.stdout

    print(get_output)

    while count < WAIT_FOR_ARTIFACT_TIMEOUT and "not found" in get_output:
        print(f"Waiting for {artifact_type}/{artifact_name} in {namespace} to exist. Wait count: {count}")
        count += 1
        get_output = run_command(["kubectl", "-n", namespace, "get", f"{artifact_type}/{artifact_name}"], ignore_errors=True)
        # if artifact does not exist, important output will be in stderr
        # if artifact DOES exist, use stdout
        if get_output.stderr != "":
            get_output = get_output.stderr
        else:
            get_output = get_output.stdout
        print(get_output)
        time.sleep(1)

def get_otel_collector_endpoint():
    return OPENTELEMETRY_COLLECTOR_ENDPOINT

def get_github_org(github_repo):
    return github_repo[:github_repo.index("/")]

def hash_string(input_str, charset="UTF-8", algorithm="SHA256"):
    hash_factory = hashlib.new(algorithm)
    hash_factory.update(input_str.encode(charset))
    return hash_factory.hexdigest()

##############################
# DT FUNCTIONS

def build_dt_urls(dt_env, dt_env_name):
    if dt_env.lower() == "live":
        dt_tenant_apps = f"https://{dt_env_name}.apps.dynatrace.com"
        dt_tenant_live = f"https://{dt_env_name}.live.dynatrace.com"
    else:
      dt_tenant_apps = f"https://{dt_env_name}.{dt_env}.apps.dynatrace.com"
      dt_tenant_live = f"https://{dt_env_name}.{dt_env}.dynatrace.com"

    # if environment is "dev" or "sprint"
    # ".dynatracelabs.com" not ".dynatrace.com"
    if dt_env.lower() == "dev" or dt_env.lower() == "sprint":
        dt_tenant_apps = dt_tenant_apps.replace(".dynatrace.com", ".dynatracelabs.com")
        dt_tenant_live = dt_tenant_live.replace(".dynatrace.com", ".dynatracelabs.com")
    
    return dt_tenant_apps, dt_tenant_live

def get_sso_token_url(dt_env):
    if dt_env.lower() == "dev":
        return SSO_TOKEN_URL_DEV
    elif dt_env.lower() == "sprint":
        return SSO_TOKEN_URL_SPRINT
    elif dt_env.lower() == "live":
        return SSO_TOKEN_URL_LIVE
    else:
        return None

def get_sso_auth_token(sso_token_url, oauth_client_id, oauth_client_secret, oauth_urn, permissions):
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    oauth_body = {
        "grant_type": "client_credentials",
        "client_id": oauth_client_id,
        "client_secret": oauth_client_secret,
        "resource": oauth_urn,
        "scope": permissions
    }

    ##############################
    # Step 1: Get Access Token
    ##############################
    access_token_resp = requests.post(
        url=sso_token_url,
        data=oauth_body
    )

    if access_token_resp.status_code != 200:
        print(f"{access_token_resp.json()}")
        return "OAuth error occurred. Data NOT sent. Please investigate."

    access_token_json = access_token_resp.json()
    access_token_value = access_token_json['access_token']

    return access_token_value

def create_dt_api_token(token_name, scopes, dt_rw_api_token, dt_tenant_live):

    # Automatically expire tokens 1 day in future.
    time_future = datetime.datetime.now() + datetime.timedelta(days=1)
    expiry_date = time_future.strftime("%Y-%m-%dT%H:%M:%S.999Z")

    headers = {
        "accept": "application/json; charset=utf-8",
        "content-type": "application/json; charset=utf-8",
        "authorization": f"api-token {dt_rw_api_token}"
    }

    payload = {
        "name": token_name,
        "scopes": scopes,
        "expirationDate": expiry_date
    }

    resp = requests.post(
        url=f"{dt_tenant_live}/api/v2/apiTokens",
        headers=headers,
        json=payload
    )

    if resp.status_code != 201:
        exit(f"Cannot create DT API token: {token_name}. Response was: {resp.status_code}. {resp.text}. Exiting.")

    return resp.json()['token']

def get_geolocation(dt_env):
    if dt_env.lower() == "dev":
        return GEOLOCATION_DEV
    elif dt_env.lower() == "sprint":
        return GEOLOCATION_SPRINT
    elif dt_env.lower() == "live":
        return GEOLOCATION_LIVE
    else:
        return None
    
def send_startup_ping():
    ## 1. Take lowercase GITHUB_ORG_SLASH_REPO and lowercase it.
    ## 2. For user privacy, calculate an irreversible one-way hash of this string
    hashed_org_slash_repo = hash_string(input_str=GITHUB_ORG_SLASH_REPOSITORY.lower(), charset="UTF-8", algorithm="SHA256")

    # Build content and send request
    url = "https://ljj95gnqj2.execute-api.us-east-1.amazonaws.com/default/ag-platform-engineering-codespace-bizevent-tracker"

    headers = {
        "User-Agent": "GitHub",
        "Content-Type": "application/json"
    }

    body = {
        "repo": hashed_org_slash_repo,
        "testing": False
    }

    resp = requests.post(
        url=url,
        headers=headers,
        json=body
    )
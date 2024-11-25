import os
from utils import *

ARGOCD_VERSION="v2.12.2"

if (
    DT_RW_API_TOKEN is None or
    DT_ENV_NAME is None or
    DT_ENV is None or
    DT_OAUTH_CLIENT_ID is None or
    DT_OAUTH_CLIENT_SECRET is None or
    DT_OAUTH_ACCOUNT_URN is None
):
    exit("Missing mandatory environment variables. Cannot proceed. Exiting.")

# Build DT environment URLs
DT_TENANT_APPS, DT_TENANT_LIVE = build_dt_urls(dt_env_name=DT_ENV_NAME, dt_env=DT_ENV)

# Get correct SSO URL
DT_SSO_TOKEN_URL = get_sso_token_url(dt_env=DT_ENV)

# Create other DT Tokens
DT_ALL_INGEST_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_ALL_INGEST_TOKEN", scopes=[
    "bizevents.ingest",
    "events.ingest",
    "logs.ingest",
    "metrics.ingest",
    "openTelemetryTrace.ingest",
    "DataExport", 
    "entities.read", 
    "settings.read", 
    "settings.write", 
    "activeGateTokenManagement.create"
], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)
DT_OP_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_OP_TOKEN", scopes=[
    "InstallerDownload",
    "DataExport", 
    "entities.read", 
    "settings.read",
    "settings.write", 
    "activeGateTokenManagement.create"
    ], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)
DT_MONACO_TOKEN = create_dt_api_token(token_name="[devrel demo] DT_MONACO_TOKEN", scopes=[
    "settings.read",
    "settings.write",
    "slo.read",
    "slo.write",
    "DataExport",
    "ExternalSyntheticIntegration",
    "ReadConfig",
    "WriteConfig"
], dt_rw_api_token=DT_RW_API_TOKEN, dt_tenant_live=DT_TENANT_LIVE)

## Keptn
# Should Keptn be installed or not?
INSTALL_KEPTN = os.environ.get("INSTALL_KEPTN", "true")

if INSTALL_KEPTN.lower() == "false" or INSTALL_KEPTN.lower() == "no":
    # Rename files to prevent installation by argoCD
    try:
        os.rename(src="gitops/applications/platform/keptn.yml", dst="gitops/applications/platform/keptn.yml.BAK")
        os.rename(src="gitops/manifests/platform/keptn/keptn-metrics.yml", dst="gitops/manifests/platform/keptn/keptn-metrics.yml.BAK")
        os.rename(src="gitops/manifests/platform/keptn/otelcol-keptnconfig.yml", dst="gitops/manifests/platform/keptn/otelcol-keptnconfig.yml.BAK")
        git_commit(target_file="-A", commit_msg="do not install Keptn", push=True)
    except:
        print("Exception caught renaming (to remove) Keptn files. No big deal. You're probably re-running this script. Continuing.")

# Set DT GEOLOCATION based on env type used
# TODO: Find a better way here. If this was widely used, all load would be on one GEOLOCATION.
DT_GEOLOCATION = get_geolocation(dt_env=DT_ENV)

###################################

# remove cluster if re-run
output = run_command(["kind", "delete", "cluster"])

###################################
# Find and replace placeholders
# Commit up to repo
# Find and replace DT_TENANT_LIVE_PLACEHOLDER with real text
# eg. "https://abc12345.live.dynatrace.com"
# Push = False for the first set
# because we push on the final git commit
do_file_replace(pattern="./**/*.y*ml", find_string="DT_TENANT_LIVE_PLACEHOLDER", replace_string=DT_TENANT_LIVE, recursive=True)
do_file_replace(pattern="./**/*.json", find_string="DT_TENANT_LIVE_PLACEHOLDER", replace_string=DT_TENANT_LIVE, recursive=True)
git_commit(target_file="-A", commit_msg="update DT_TENANT_LIVE_PLACEHOLDER", push=False)





# create kind cluster
output = run_command(["kind", "create", "cluster", "--config", ".devcontainer/kind-cluster.yml", "--wait", STANDARD_TIMEOUT])

# create namespaces
namespaces = ["argocd"]

for namespace in namespaces:
    output = run_command(["kubectl", "create", "namespace", namespace])
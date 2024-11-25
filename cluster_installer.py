import os
from utils import *

ARGOCD_VERSION="v2.12.2"

# remove cluster if re-run
output = run_command(["kind", "delete", "cluster"])

# create kind cluster
output = run_command(["kind", "create", "cluster", "--config", ".devcontainer/kind-cluster.yml", "--wait", STANDARD_TIMEOUT])

# create namespaces
namespaces = ["argocd"]

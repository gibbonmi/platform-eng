import os
from utils import *

ARGOCD_VERSION="v2.12.2"


# create kind cluster
run_command(["kind", "delete", "cluster"])

# create namespaces
namespaces = ["argocd"]

import requests
import time
from utils import *

COLLECTOR_WAIT_TIMEOUT_SECONDS = 300

# observability related tests

def test_ensure_namespaces_exists():
    output = run_command(["kubectl", "get", "namespaces"])
    assert argocd
import requests
import datetime
import subprocess
import glob
import time
import os
import json
import hashlib

SENSITIVE_WORDS = ["secret", "secrets", "token", "tokens", "generate-token"]

BACKSTAGE_PORT_NUMBER = 30105
ARGOCD_PORT_NUMBER = 30100
DEMO_APP_PORT_NUMBER = 80

STANDARD_TIMEOUT="300s"
WAIT_FOR_ARTIFACT_TIMEOUT = 60
WAIT_FOR_ACCOUNTS_TIMEOUT = 60

COLLECTOR_WAIT_TIMEOUT_SECONDS = 30

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
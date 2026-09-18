import subprocess
import os

# Initialize project context
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "cloud-gemini-dev-0")
REGION = os.environ.get("GCP_REGION", "global")  # setPublisherModelConfig typically maps under global/regional control plane

print(f"Enabling data sharing provider config for Anthropic on project {PROJECT_ID}...")

# Obtain active gcloud access token dynamically
try:
    token_proc = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True,
        text=True,
        check=True
    )
    access_token = token_proc.stdout.strip()
except Exception as e:
    print(f"Failed to retrieve gcloud access token. Ensure you are authenticated. Error: {e}")
    exit(1)

# Construct REST API call parameters
host = "https://aiplatform.googleapis.com"
url = f"{host}/v1beta1/projects/{PROJECT_ID}/locations/{REGION}/publishers/anthropic/models/claude-fable-5:setPublisherModelConfig"

import json
import urllib.request

headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

payload = {
    "publisherModelConfig": {
        "dataSharingEnabledProvider": "anthropic"
    }
}

req = urllib.request.Request(
    url, 
    data=json.dumps(payload).encode("utf-8"), 
    headers=headers, 
    method="POST"
)

try:
    with urllib.request.urlopen(req) as response:
        res_body = response.read().decode("utf-8")
        print("Successfully enabled data sharing for Claude Fable 5!")
        print(res_body)
except urllib.error.HTTPError as e:
    print(f"HTTP Error occurred: {e.code} - {e.reason}")
    print(e.read().decode("utf-8"))
except Exception as e:
    print(f"An error occurred: {e}")
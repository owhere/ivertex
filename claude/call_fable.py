import vertexai
from anthropic import AnthropicVertex
import os

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "Your_PROJECT_ID")
REGION = os.environ.get("GCP_REGION", "global")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=REGION)

# Call Claude Fable 5
client = AnthropicVertex(region=REGION, project_id=PROJECT_ID)

response = client.messages.create(
    model="claude-fable-5",
    max_tokens=4096,
    messages=[
        {"role": "user", "content": "Analyze this deployment script for security risks."}
    ],
)

print(response.content)
#/bin/bash

# 1. Clear any ghost API keys that might be cached
unset GEMINI_API_KEY
unset GOOGLE_API_KEY

# 2. Tell the tool explicitly to use Vertex AI
export GOOGLE_GENAI_USE_VERTEXAI=true

# 3. Point to your specific project and the 'global' region
export GOOGLE_CLOUD_PROJECT="ox-vgg-wise-research-dev-0"
export GOOGLE_CLOUD_LOCATION="global"

# 4. Launch the tool with the 3.1 model
gemini -m gemini-3.1-pro-preview


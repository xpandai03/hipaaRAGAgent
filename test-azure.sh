#!/bin/bash

# Test Azure OpenAI deployment
# Replace DEPLOYMENT_NAME with your actual deployment name from Azure Portal

DEPLOYMENT_NAME="gpt-5-mini"
ENDPOINT="https://adavi-mf694jmx-eastus2.cognitiveservices.azure.com"
API_KEY="YOUR_AZURE_API_KEY_HERE"

echo "Testing deployment: $DEPLOYMENT_NAME"
echo "================================"

curl -X POST "$ENDPOINT/openai/deployments/$DEPLOYMENT_NAME/chat/completions?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "api-key: $API_KEY" \
  -d '{
    "messages": [{"role": "user", "content": "Hello, please respond with: I am working!"}],
    "temperature": 0.7,
    "max_tokens": 50
  }' | python3 -m json.tool
#!/bin/bash

# Simple script to test sending a message to Telegram
SERVICE_URL="${SERVICE_URL:-}"
API_KEY="${API_KEY:-}"

# Check if required environment variables are set
if [ -z "$SERVICE_URL" ]; then
    echo "Error: SERVICE_URL environment variable is not set"
    echo "Please set it with: export SERVICE_URL=your_service_url_here"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY environment variable is not set"
    echo "Please set it with: export API_KEY=your_api_key_here"
    exit 1
fi

echo "Testing Telegram message service..."
echo "Service URL: $SERVICE_URL"
echo

# Test message
MESSAGE="Hello from Cloud Run! $(date)"

echo "Sending message: $MESSAGE"
echo

curl -X POST "$SERVICE_URL" \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"message\": \"$MESSAGE\"}" \
  -w "\nStatus: %{http_code}\n"

echo
echo "Check your Telegram for the message!"
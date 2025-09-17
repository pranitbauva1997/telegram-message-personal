#!/bin/bash

# Configuration
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

echo "=== Testing Telegram Message Service ==="
echo "Service URL: $SERVICE_URL"
echo "API Key: [SET]"
echo

# Test 1: Health Check
echo "1. Testing Health Check (/health):"
curl -s -X GET "$SERVICE_URL/health" | jq . 2>/dev/null || curl -s -X GET "$SERVICE_URL/health"
echo -e "\n"

# Test 2: Debug Info
echo "2. Testing Debug Info (/debug):"
curl -s -X GET "$SERVICE_URL/debug" | jq . 2>/dev/null || curl -s -X GET "$SERVICE_URL/debug"
echo -e "\n"

# Test 2.5: Bot Test
echo "2.5. Testing Bot Configuration (/test):"
curl -s -X GET \
  -H "x-api-key: $API_KEY" \
  "$SERVICE_URL/test" | jq . 2>/dev/null || curl -s -X GET \
  -H "x-api-key: $API_KEY" \
  "$SERVICE_URL/test"
echo -e "\n"

# Test 3: Send Message (root endpoint)
echo "3. Testing Send Message (/):"
curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message from root endpoint"}' \
  "$SERVICE_URL" | jq . 2>/dev/null || curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message from root endpoint"}' \
  "$SERVICE_URL"
echo -e "\n"

# Test 4: Send Message (/send endpoint)
echo "4. Testing Send Message (/send):"
curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message from /send endpoint"}' \
  "$SERVICE_URL/send" | jq . 2>/dev/null || curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message from /send endpoint"}' \
  "$SERVICE_URL/send"
echo -e "\n"

# Test 5: Invalid endpoint
echo "5. Testing Invalid Endpoint (/invalid):"
curl -s -X GET "$SERVICE_URL/invalid" | jq . 2>/dev/null || curl -s -X GET "$SERVICE_URL/invalid"
echo -e "\n"

# Test 8: Test without API key
echo "8. Testing Bot Test without API Key (/test):"
curl -s -X GET "$SERVICE_URL/test" | jq . 2>/dev/null || curl -s -X GET "$SERVICE_URL/test"
echo -e "\n"

# Test 6: Missing API key
echo "6. Testing Missing API Key:"
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message without API key"}' \
  "$SERVICE_URL" | jq . 2>/dev/null || curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message without API key"}' \
  "$SERVICE_URL"
echo -e "\n"

# Test 7: Invalid JSON
echo "7. Testing Invalid JSON:"
curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d 'invalid json' \
  "$SERVICE_URL" | jq . 2>/dev/null || curl -s -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d 'invalid json' \
  "$SERVICE_URL"
echo -e "\n"

echo "=== Test Complete ==="

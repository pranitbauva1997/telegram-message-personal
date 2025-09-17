# Telegram Message Sender

This is a Google Cloud Run service that sends messages to Telegram using the Bot API and Functions Framework.

I have a bunch of services/cron jobs running and I like to be notified if something failed on my phone. This simple utility does the job perfectly.

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token you receive

### 2. Get Your Chat ID

1. Start a conversation with your bot
2. Send a message to the bot
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Find your chat ID in the response

### 3. Environment Variables

Set the following environment variables:

- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
- `TELEGRAM_CHAT_ID`: Your chat ID (where messages will be sent)
- `API_KEY`: API key for authentication
- `PORT`: Port for the service (default: 8080)

### 4. Deployment

Build and deploy to Google Cloud Run:

```bash
gcloud run deploy telegram-message-personal \
  --source . \
  --platform managed \
  --region europe-west1 \
  --set-env-vars TELEGRAM_BOT_TOKEN=your_bot_token,TELEGRAM_CHAT_ID=your_chat_id,API_KEY=your_api_key \
  --allow-unauthenticated
```

### 5. Testing

Use the provided test script:

```bash
./test.sh
```

Or manually:

```bash
curl -X POST \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}' \
  https://your-service-url
```

## API

### POST /

Send a message to Telegram.

**Headers:**
- `x-api-key`: Your API key
- `Content-Type`: application/json

**Body:**
```json
{
  "message": "Your message here"
}
```

**Response:**
```json
{
  "message": "Message sent successfully"
}
```

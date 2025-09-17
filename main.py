import functions_framework
from flask import Response
import json
import os
import urllib.request
import urllib.parse
import urllib.error

@functions_framework.http
def send_telegram_message(request):
    """
    HTTP Cloud Function to send a message via Telegram Bot API.
    Args:
        request (flask.Request): The request object.
    Returns:
        Response: JSON response with status code and message.
    """
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    api_key = os.environ.get('API_KEY')

    if not bot_token or not chat_id or not api_key:
        return Response(
            response=json.dumps({'message': 'Missing required environment variables'}),
            status=500,
            mimetype='application/json'
        )

    # Check x-api-key header
    if request.headers.get('x-api-key') != api_key:
        return Response(
            response=json.dumps({'message': 'Invalid or missing x-api-key header'}),
            status=401,
            mimetype='application/json'
        )

    # Parse JSON body
    request_json = request.get_json(silent=True)
    if not request_json or 'message' not in request_json or not isinstance(request_json['message'], str) or not request_json['message'].strip():
        return Response(
            response=json.dumps({'message': 'Invalid or missing "message" field in JSON body'}),
            status=400,
            mimetype='application/json'
        )

    message = request_json['message']

    try:
        # Send message via Telegram Bot API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'  # Optional: allows basic HTML formatting
        }

        # Convert payload to URL-encoded data
        data = urllib.parse.urlencode(payload).encode('utf-8')

        # Create request with timeout
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')

        with urllib.request.urlopen(req, timeout=10) as response:
            response_data = json.loads(response.read().decode('utf-8'))

            if response_data.get('ok'):
                return Response(
                    response=json.dumps({'message': 'Message sent successfully'}),
                    status=200,
                    mimetype='application/json'
                )
            else:
                error_message = response_data.get('description', 'Unknown error')
                return Response(
                    response=json.dumps({'message': f'Failed to send message: {error_message}'}),
                    status=500,
                    mimetype='application/json'
                )

    except urllib.error.URLError as e:
        if hasattr(e, 'reason') and 'timeout' in str(e.reason).lower():
            return Response(
                response=json.dumps({'message': 'Request timed out'}),
                status=500,
                mimetype='application/json'
            )
        else:
            return Response(
                response=json.dumps({'message': f'Network error: {str(e)}'}),
                status=500,
                mimetype='application/json'
            )
    except Exception as e:
        return Response(
            response=json.dumps({'message': f'Internal error: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

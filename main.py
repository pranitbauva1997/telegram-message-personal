import functions_framework
from flask import Response, request as flask_request
import json
import os
import urllib.request
import urllib.parse
import urllib.error
import logging
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

@functions_framework.http
def health_check(request):
    """
    Health check endpoint to verify service is running.
    """
    logger.info(f"Health check requested from {request.remote_addr}")

    return Response(
        response=json.dumps({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'telegram-message-personal',
            'version': '1.0.0'
        }),
        status=200,
        mimetype='application/json'
    )

@functions_framework.http
def debug_info(request):
    """
    Debug endpoint to show environment and configuration info.
    """
    logger.info(f"Debug info requested from {request.remote_addr}")

    debug_data = {
        'timestamp': datetime.now().isoformat(),
        'environment': {
            'TELEGRAM_BOT_TOKEN': 'Set' if os.environ.get('TELEGRAM_BOT_TOKEN') else 'NOT SET',
            'TELEGRAM_CHAT_ID': 'Set' if os.environ.get('TELEGRAM_CHAT_ID') else 'NOT SET',
            'API_KEY': 'Set' if os.environ.get('API_KEY') else 'NOT SET',
            'PORT': os.environ.get('PORT', '8080'),
            'GOOGLE_CLOUD_PROJECT': os.environ.get('GOOGLE_CLOUD_PROJECT', 'NOT SET')
        },
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'files_in_directory': os.listdir('.'),
        'request_info': {
            'method': request.method,
            'url': request.url,
            'path': request.path,
            'remote_addr': request.remote_addr,
            'headers': dict(request.headers)
        }
    }

    return Response(
        response=json.dumps(debug_data, indent=2),
        status=200,
        mimetype='application/json'
    )

@functions_framework.http
def telegram_service(request):
    """
    Main HTTP Cloud Function with routing for different endpoints.
    Args:
        request (flask.Request): The request object.
    Returns:
        Response: JSON response with status code and message.
    """
    # Comprehensive request logging
    logger.info("=" * 80)
    logger.info(f"REQUEST RECEIVED at {datetime.now().isoformat()}")
    logger.info(f"Method: {request.method}")
    logger.info(f"URL: {request.url}")
    logger.info(f"Path: {request.path}")
    logger.info(f"Query String: {request.query_string.decode('utf-8') if request.query_string else 'None'}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Remote Address: {request.remote_addr}")
    logger.info(f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
    logger.info(f"Content Type: {request.headers.get('Content-Type', 'Unknown')}")
    logger.info(f"Content Length: {request.headers.get('Content-Length', 'Unknown')}")

    # Log request body safely
    try:
        if request.is_json:
            body_data = request.get_json(silent=True)
            logger.info(f"JSON Body: {json.dumps(body_data, indent=2) if body_data else 'Invalid JSON'}")
        else:
            body_content = request.get_data(as_text=True)
            logger.info(f"Raw Body: {body_content[:500]}{'...' if len(body_content) > 500 else ''}")
    except Exception as e:
        logger.error(f"Error reading request body: {str(e)}")

    logger.info("=" * 80)

    # Route based on path
    path = request.path.strip('/')

    if path == '' or path == 'send':
        return send_telegram_message(request)
    elif path == 'health':
        return health_check(request)
    elif path == 'debug':
        return debug_info(request)
    else:
        logger.warning(f"Unknown path requested: {path}")
        return Response(
            response=json.dumps({
                'message': f'Unknown endpoint: {path}',
                'available_endpoints': ['/', '/send', '/health', '/debug']
            }),
            status=404,
            mimetype='application/json'
        )

def send_telegram_message(request):
    """
    Send a message via Telegram Bot API.
    Args:
        request (flask.Request): The request object.
    Returns:
        Response: JSON response with status code and message.
    """
    logger.info("Processing send_telegram_message request")

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    api_key = os.environ.get('API_KEY')

    # Log environment variable status (without revealing values)
    logger.info("Environment variables check:")
    logger.info(f"TELEGRAM_BOT_TOKEN: {'Set' if bot_token else 'NOT SET'}")
    logger.info(f"TELEGRAM_CHAT_ID: {'Set' if chat_id else 'NOT SET'}")
    logger.info(f"API_KEY: {'Set' if api_key else 'NOT SET'}")

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
        logger.info(f"Telegram API URL: {url}")
        logger.info(f"Chat ID: {chat_id}")
        logger.info(f"Message length: {len(message)}")

        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'  # Optional: allows basic HTML formatting
        }
        logger.debug(f"Telegram payload: {payload}")

        # Convert payload to URL-encoded data
        data = urllib.parse.urlencode(payload).encode('utf-8')
        logger.debug(f"Encoded data length: {len(data)}")

        # Create request with timeout
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/x-www-form-urlencoded')
        logger.info("Making request to Telegram API...")

        with urllib.request.urlopen(req, timeout=10) as response:
            logger.info(f"Telegram API response status: {response.status}")
            logger.info(f"Telegram API response headers: {dict(response.headers)}")
            response_content = response.read().decode('utf-8')
            logger.info(f"Telegram API raw response: {response_content}")
            response_data = json.loads(response_content)

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
        logger.error(f"Unexpected error in send_telegram_message: {str(e)}", exc_info=True)
        logger.error(f"Request details: method={request.method}, url={request.url}, headers={dict(request.headers)}")
        return Response(
            response=json.dumps({
                'message': f'Internal error: {str(e)}',
                'error_type': type(e).__name__,
                'timestamp': datetime.now().isoformat()
            }),
            status=500,
            mimetype='application/json'
        )

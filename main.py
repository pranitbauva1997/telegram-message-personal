import functions_framework
from flask import Response
import json
import os
import asyncio
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import SendMessageRequest
from telethon.tl.types import InputPeerUserFromMessage, PeerUser

@functions_framework.http
def send_telegram_message(request):
    """
    HTTP Cloud Function to send a message to a Telegram user.
    Args:
        request (flask.Request): The request object.
    Returns:
        Response: JSON response with status code and message.
    """
    api_id = os.environ.get('TELEGRAM_API_ID')
    api_hash = os.environ.get('TELEGRAM_API_HASH')
    phone = os.environ.get('TELEGRAM_PHONE')
    api_key = os.environ.get('API_KEY')

    if not api_id or not api_hash or not phone:
        return Response(
            response=json.dumps({'message': 'Missing environment variables'}),
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
        # Initialize Telethon client
        async def send_message():
            async with TelegramClient('user_session', int(api_id), api_hash) as client:
                # Ensure client is authorized
                if not await client.is_user_authorized():
                    try:
                        await client.start(phone=phone)
                    except Exception as e:
                        return {'success': False, 'error': f'Authentication failed: {str(e)}'}

                # Resolve recipient
                recipient_phone = phone
                try:
                    user = await client.get_entity(recipient_phone)
                except ValueError:
                    return {'success': False, 'error': f'User with phone {recipient_phone} not found or not a Telegram contact'}

                # Send message
                await client(SendMessageRequest(
                    peer=user,
                    message=message
                ))
                return {'success': True, 'error': None}

        # Run async function
        result = asyncio.run(send_message())

        if not result['success']:
            return Response(
                response=json.dumps({'message': result['error']}),
                status=500,
                mimetype='application/json'
            )

        return Response(
            response=json.dumps({'message': 'successful'}),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        return Response(
            response=json.dumps({'message': f'Internal error: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

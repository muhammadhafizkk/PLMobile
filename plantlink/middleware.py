# myapp/middleware.py
from django.http import JsonResponse
from jwt import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
import jwt

JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = settings.JWT_ALGORITHM

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('Authorization')
        if token:
            try:
                # Decode the token
                payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
                request.user_id = payload['user_id']  # Set user_id for the request
            except ExpiredSignatureError:
                return JsonResponse({'success': False, 'error': 'Token expired'}, status=401)
            except InvalidTokenError:
                return JsonResponse({'success': False, 'error': 'Invalid token'}, status=401)
        else:
            request.user_id = None  # Anonymous user
        return self.get_response(request)


# Existing middleware:
class XFrameOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = "frame-ancestors 'self' http://localhost:8000 https://5e03-161-139-102-63.ngrok-free.app"  # Adjust the port if necessary
        return response

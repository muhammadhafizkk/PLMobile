from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
import json
import requests
import jwt
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.conf import settings

def home(request): 
    # return render(request, 'home.html')
    return JsonResponse({'message': 'This is the backend for the PlantLink mobile app.'})

@csrf_exempt
def logPlantFeed(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required'}, status=400)

            # Direct validation for the specified credentials
            if email == 'hafiy@gmail.com' and password == 'hafiyhakimi11':
                # Example response for valid login
                return JsonResponse({
                    'message': 'Login successful',
                    'user': {
                        'username': 'hafiy',
                        'email': 'hafiy@gmail.com',
                        'userlevel': 'manager',
                        'userid': 1,  
                        'name': 'Hafiy Hakimi',
                    }
                })
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

# Define a secret key (Use Django's SECRET_KEY or a separate one for JWT)
JWT_SECRET_KEY = settings.SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_TIME = timedelta(hours=1)  # Token expires in 1 hour

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        # Authenticate the user
        user = authenticate(username=email, password=password)
        if user:
            # Create a token
            payload = {
                'user_id': user.id,
                'email': user.email,
                'exp': datetime.now() + JWT_EXPIRATION_TIME
            }
            token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

            # Return the token to the client
            return JsonResponse({'success': True, 'token': token}, status=200)
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)

@csrf_exempt
def logout(request):
    return JsonResponse({'message': 'Logged out successfully'}, status=200)

@csrf_exempt
def profile(request):
    # validate a token or session here
    user_data = {
        'username': 'hafiy',  
        'email': 'hafiy@gmail.com',
        'userlevel': 'manager',
        'userid': 1,
        'name': 'Hafiy'
    }
    return JsonResponse({'user': user_data}, status=200)

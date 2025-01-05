import datetime
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from plantlink.mongo_setup import connect_to_mongodb
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channel.serializers import ChannelSerializer
from bson import ObjectId
import json

def index(request):
    return HttpResponse("dashboard")
# Helper function to convert ObjectId to string recursively
def convert_objectid_to_str(data):
    if isinstance(data, list):  # If the data is a list, apply to each item
        return [convert_objectid_to_str(item) for item in data]
    elif isinstance(data, dict):  # If the data is a dictionary, apply to each value
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):  # If it's an ObjectId, convert it to string
        return str(data)
    return data  # Return the data if it's neither a list, dict, nor ObjectId

def get_channel_statistics(request):
    if request.method == 'GET':
        try:
            # Connect to MongoDB
            db, collection = connect_to_mongodb('Channel', 'dashboard')
            
            # Get total channels
            total_channels = collection.count_documents({})
            
            # Get total sensors
            total_sensors = sum([
                len(channel.get('sensor', []))
                for channel in collection.find({}, {'sensor': 1})
            ])
            
            # Get total public channels
            public_channels = collection.count_documents({'privacy': 'public'})
            
            # Return the statistics
            return JsonResponse({
                "totalChannels": total_channels,
                "totalSensors": total_sensors,
                "publicChannels": public_channels
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

class ChannelList(APIView):
    def get(self, request):
        # Connect to MongoDB
        db, collection = connect_to_mongodb('Channel', 'dashboard')
        
        if collection is not None:
            channels = list(collection.find())  # Fetch all channels from MongoDB

            # Convert ObjectId to string in the fetched data
            channels = convert_objectid_to_str(channels)

            # Serialize the data using the ChannelSerializer
            serializer = ChannelSerializer(channels, many=True)

            # Return the serialized data as a response
            return Response(serializer.data)
        else:
            return Response({"error": "Failed to connect to MongoDB"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        # Validate incoming data using the ChannelSerializer
        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            # If valid, insert the data directly into MongoDB
            db, collection = connect_to_mongodb('Channel', 'dashboard')
            if collection is not None:
                collection.insert_one(serializer.validated_data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": "Failed to connect to MongoDB"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
def create_channel(request):
    if request.method == 'POST':
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)

            # Extract channel details
            channel_name = data.get('channel_name')
            description = data.get('description')
            location = data.get('location')
            privacy = data.get('privacy')

            # Validation (optional, can be improved further)
            if not channel_name or not description or not location or not privacy:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            # Connect to MongoDB
            db, collection = connect_to_mongodb('Channel', 'dashboard')

            # Check if a channel with the same name already exists
            if collection.find_one({"channel_name": channel_name}):
                return JsonResponse(
                    {'error': 'A channel with this name already exists.'},
                    status=400
                )

            # Insert into MongoDB with formatted date
            now = datetime.datetime.now()
            formatted_date = now.strftime("%d/%m/%Y")  # Format to DD/MM/YYYY
            channel = {
                "channel_name": channel_name,
                "description": description,
                "location": location,
                "privacy": privacy,
                "date_created": formatted_date,
                "date_modified": formatted_date,
                "allow_API": "",
                "API_KEY": "",
                "user_id": "",
                "sensor": []  # Initialize with an empty sensor list
            }
            collection.insert_one(channel)

            return JsonResponse({'message': 'Channel created successfully'}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def update_channel(request, channel_id):
    if request.method == 'PUT':
        try:
            # Parse the incoming data
            data = json.loads(request.body)
            channel_name = data.get('channel_name')

            if not channel_name:
                return JsonResponse({'error': 'Channel name is required.'}, status=400)

            # Connect to MongoDB
            db, collection = connect_to_mongodb('Channel', 'dashboard')

            existing_channel = collection.find_one({
                "channel_name": channel_name,
                "_id": {"$ne": ObjectId(channel_id)}  # Exclude the current channel from the check
            })
            
            # Check if a channel with the same name already exists
            if existing_channel:
                return JsonResponse(
                    {'error': 'A channel with this name already exists.'},
                    status=400
                )

            # Find the channel and update it
            now = datetime.datetime.now()
            formatted_date = now.strftime("%d/%m/%Y")
            result = collection.update_one(
                {"_id": ObjectId(channel_id)},  # Match the channel by its ID
                {"$set": {
                    "channel_name": data.get('channel_name'),
                    "description": data.get('description'),
                    "location": data.get('location'),
                    "privacy": data.get('privacy'),
                    "date_modified": formatted_date
                }}
            )

            if result.matched_count == 0:
                return JsonResponse({'error': 'Channel not found'}, status=404)

            return JsonResponse({'message': 'Channel updated successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def delete_channel(request, channel_id):
    if request.method == 'DELETE':
        try:
            # Connect to MongoDB
            db, collection = connect_to_mongodb('Channel', 'dashboard')

            # Find the channel by ID and delete it
            result = collection.delete_one({"_id": ObjectId(channel_id)})

            if result.deleted_count == 0:
                return JsonResponse({'error': 'Channel not found'}, status=404)

            return JsonResponse({'message': 'Channel deleted successfully'}, status=200)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

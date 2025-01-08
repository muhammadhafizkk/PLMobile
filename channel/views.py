from datetime import datetime, time
import os
from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import joblib
import pandas as pd
import requests
from plantlink.mongo_setup import connect_to_mongodb
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channel.serializers import ChannelSerializer
from bson import ObjectId
import json

import pytz

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

#test

# To train model - DONE
def load_trained_model():
    model_path = os.path.join('static', 'dashboard', 'best_random_forest_model.pkl')
    # model_path = '/home/shiroooo/PlantLink/static/dashboard/best_random_forest_model.pkl'
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            return model
        except Exception as e:
            print("Error loading the trained model:", str(e))
            return None
    else:
        print("Model file not found.")
        return None

# To render dashboard data dynamically - DONE
def getDashboardData(request, channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            API_KEY = channel.get('API_KEY', '')
            if not API_KEY:
                return JsonResponse({"success": False, "error": "No API_KEY found for the channel"})
            
            ph_values = []
            timestamps = []
            rainfall_values = []
            rainfall_timestamps = []
            humid_values = []
            temp_values = []
            nitrogen_values = []
            potassium_values = []
            phosphorous_values = []
            timestamps_humid_temp = []
            timestamps_NPK = []
            
            # Fetch data from sensor:DHT11
            db_humid_temp, collection_humid_temp = connect_to_mongodb('sensor', 'DHT11')
            if db_humid_temp is not None and collection_humid_temp is not None:
                humid_temp_data = collection_humid_temp.find_one({"API_KEY": API_KEY})
                if humid_temp_data:
                    for data_point in humid_temp_data.get('sensor_data', []):
                        humidity_value = data_point.get('humidity_value', '')
                        temperature_value = data_point.get('temperature_value', '')
                        
                        humid_values.append(humidity_value)
                        temp_values.append(temperature_value)

                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        timestamps_humid_temp.append(formatted_timestamp)
            # Fetch data from sensor:NPK
            db_NPK, collection_NPK = connect_to_mongodb('sensor', 'NPK')
            if db_NPK is not None and collection_NPK is not None:
                NPK_data = collection_NPK.find_one({"API_KEY": API_KEY})
                if NPK_data:
                    for data_point in NPK_data.get('sensor_data', []):
                        nitrogen_value = data_point.get('nitrogen_value', '')
                        phosphorous_value = data_point.get('phosphorous_value', '')
                        potassium_value = data_point.get('potassium_value', '')
                        
                        nitrogen_values.append(nitrogen_value)
                        phosphorous_values.append(phosphorous_value)
                        potassium_values.append(potassium_value)
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        timestamps_NPK.append(formatted_timestamp)
            
            # Fetch data from sensor:PHSensor
            db_ph, collection_ph = connect_to_mongodb('sensor', 'PHSensor')
            if db_ph is not None and collection_ph is not None:
                ph_data = collection_ph.find_one({"API_KEY": API_KEY})
                if ph_data:
                    for data_point in ph_data.get('sensor_data', []):
                        ph_values.append(data_point.get('ph_value', ''))
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        timestamps.append(formatted_timestamp)
            # Fetch data from sensor:rainfallSensor
            db_rainfall, collection_rainfall = connect_to_mongodb('sensor', 'rainfall')
            if db_rainfall is not None and collection_rainfall is not None:
                rainfall_data = collection_rainfall.find_one({"API_KEY": API_KEY})
                if rainfall_data:
                    for data_point in rainfall_data.get('sensor_data', []):
                        rainfall_values.append(data_point.get('rainfall_value', ''))
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        rainfall_timestamps.append(formatted_timestamp)
            
            context = {
                "channel_id": channel_id,
                "ph_values": ph_values,
                "rainfall_values": rainfall_values,
                "timestamps": timestamps,
                "humid_values": humid_values,
                "temp_values": temp_values,
                "timestamps_humid_temp": timestamps_humid_temp,
                "timestamps_NPK":timestamps_NPK,
                "rainfall_timestamps":rainfall_timestamps,
                "nitrogen_values":nitrogen_values,
                "phosphorous_values":phosphorous_values,
                "potassium_values":potassium_values,
                "API": API_KEY,
            }
            if humid_values or ph_values or rainfall_values or nitrogen_values or potassium_values or phosphorous_value or temp_values:
                # Load the trained Random Forest model
                model = load_trained_model()
                if model:
                    # Prepare input data for model prediction
                    input_data = {
                        'N': float(nitrogen_values[-1]) if nitrogen_values else 0.0,  
                        'P': float(potassium_values[-1]) if potassium_values else 0.0,
                        'K': float(phosphorous_values[-1]) if phosphorous_values else 0.0,
                        'temperature': float(temp_values[-1]) if temp_values else 0.0,  
                        'humidity': float(humid_values[-1]) if humid_values else 0.0,  
                        'ph': float(ph_values[-1]) if ph_values else 0.0,  
                        'rainfall':float(rainfall_values[-1]) if rainfall_values else 0.0,   
                    }

                    input_df = pd.DataFrame([input_data])

                    # Make predictions using the model
                    prediction = model.predict(input_df)
                    
                    probabilities = model.predict_proba(input_df)
                    
                    labels = model.classes_

                    # Combine the labels with their probabilities and sort them by probability in descending order
                    crop_recommendations = [
                        {"crop": label, "accuracy": prob * 100}  # Convert to percentage
                        for label, prob in zip(labels, probabilities[0])
                    ]
                    crop_recommendations.sort(key=lambda x: x["accuracy"], reverse=True)
                    # Add the crop recommendation to the context
                    context["crop_recommendations"] = crop_recommendations

                return JsonResponse(context)
                
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")
        return JsonResponse({"success": False, "error": "Database connection error"})
    
# DECLARE PLANTFEED URL HERE
PLANTFEED_SHARING_URL="https://9e0c-2405-3800-836-2945-8c2c-9ccf-aee7-eed8.ngrok-free.app/"
PLANTFEED_SHARING_API_PATH=PLANTFEED_SHARING_URL+"group/PlantLink-Graph-API"
    
@csrf_exempt
def share_chart(request, channel_id, chart_type, start_date, end_date, chart_name):
    try:
        _id = ObjectId(channel_id)
        db, collection = connect_to_mongodb('Channel', 'dashboard')
        if db is None or collection is None:
            return JsonResponse({"error": "Failed to connect to MongoDB."}, status=500)

        channel = collection.find_one({"_id": _id})
        if not channel:
            return JsonResponse({"error": "Channel not found."}, status=404)

        plantfeed_link = PLANTFEED_SHARING_API_PATH
        embed_link = f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/{chart_type}Chart/{start_date}/{end_date}/"
        
        # Format the data according to PlantFeed's expected structure
        channel_data = {
            "userid": "1",  # Make sure this matches a valid user ID in PlantFeed
            "chart_name": chart_name,
            "chart_type": chart_type,
            "start_date": start_date,
            "end_date": end_date,
            "embed_link": embed_link,
        }

        # Add headers to ensure proper JSON content type
        headers = {
            'Content-Type': 'application/json',
        }

        response = requests.post(
            plantfeed_link, 
            json=channel_data,  # Use json parameter instead of data
            headers=headers
        )

        print("Sending data:", channel_data)
        print("Response:", response.text)


        if response.status_code == 200:
            return JsonResponse({"success": f"{chart_type} chart successfully sent to PlantFeed."}, status=200)
        else:
            return JsonResponse({
                "error": f"Failed to share {chart_type} chart. PlantFeed Response: {response.text}",
                "status_code": response.status_code
            }, status=500)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

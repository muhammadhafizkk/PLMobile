#VIEWS OF AZIZ'S PARTS
import json
from django.shortcuts import redirect, render
from bson import ObjectId
from django.http import HttpResponse, JsonResponse
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import *
from plantlink.mongo_setup import connect_to_mongodb
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import pytz
import joblib
import os

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
    
def connect_and_find(collection_name, api_key):
    db, collection = connect_to_mongodb('sensor', collection_name)
    if db is not None and collection is not None:
        return collection.find_one({"API_KEY": api_key})
    return None

def get_channel_details(channel):
    return {
        "channel_name": channel.get('channel_name', ''),
        "description": channel.get('description', ''),
        "sensor": channel.get('sensor', ''),
        "API": channel.get("API_KEY", ''),
        "allow_api": channel.get("allow_API", ''),
        "soil_location": channel.get("location", ''),
        "privacy": channel.get("privacy", '')
    }

def calculate_graph_count(api_key):
    sensor_collections = {
        'DHT11': 2,
        'NPK': 3,
        'PHSensor': 1,
        'rainfall': 1
    }
    graph_count = 0
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(connect_and_find, collection, api_key): weight for collection, weight in sensor_collections.items()}
        for future in futures:
            if future.result():
                graph_count += futures[future]
    return graph_count

def view_channel_sensor(request, channel_id):
    if 'username' not in request.COOKIES:
        return redirect('logPlantFeed')
    
    start_time = time.time()
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is None or collection is None:
        print("Error connecting to MongoDB.")
        return JsonResponse({"success": False, "error": "Error connecting to MongoDB"}, status=500)
    
    channel = collection.find_one({"_id": _id})
    if not channel:
        return JsonResponse({"success": False, "error": "Document not found"}, status=404)

    print("Found channel")
    channel_details = get_channel_details(channel)
    graph_count = calculate_graph_count(channel_details["API"])

    context = {
        "channel_name": channel_details["channel_name"],
        "description": channel_details["description"],
        "channel_id": channel_id,
        "API": channel_details["API"],
        "graph_count": graph_count,
        "allow_api": channel_details["allow_api"],
        "soil_location": channel_details["soil_location"],
        "privacy": channel_details["privacy"]
    }

    end_time = time.time()
    print("Execution time: {:.2f} seconds".format(end_time - start_time))

    return render(request, 'dashboard_page.dart', context) # dashboard.html


# To view embedded code dashboard
def render_embed_code(request, channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            channel_privacy = channel.get('privacy', '')
            if channel_privacy == "public":
                print("Found channel")
                channel_name = channel.get('channel_name', '')
                description = channel.get('description', '')
                API_KEY = channel.get('API_KEY', '')
                soil_location=channel.get("location", '')
                graph_count = 0

                if API_KEY:
                    # Check sensors in DHT11
                    dht_db, dht_collection = connect_to_mongodb('sensor', 'DHT11')
                    if dht_db is not None and dht_collection is not None:
                        dht_sensor = dht_collection.find_one({"API_KEY": API_KEY})
                        if dht_sensor:
                            graph_count += 2

                    # Check sensors in NPK
                    NPK_db, NPK_collection = connect_to_mongodb('sensor', 'NPK')
                    if NPK_db is not None and NPK_collection is not None:
                        NPK_sensor = NPK_collection.find_one({"API_KEY": API_KEY})
                        if NPK_sensor:
                            graph_count += 3

                    # Check sensors in PHSensor
                    ph_db, ph_collection = connect_to_mongodb('sensor', 'PHSensor')
                    if ph_db is not None and ph_collection is not None:
                        ph_sensor = ph_collection.find_one({"API_KEY": API_KEY})
                        if ph_sensor:
                            graph_count += 1

                    # Check sensors in rainfallSensor
                    rainfall_db, rainfall_collection = connect_to_mongodb('sensor', 'rainfall')
                    if rainfall_db is not None and ph_collection is not None:
                        rainfall_sensor = rainfall_collection.find_one({"API_KEY": API_KEY})
                        if rainfall_sensor:
                            graph_count += 1
                context = {
                    "channel_name": channel_name,
                    "description": description,
                    "channel_id": channel_id,
                    "API": API_KEY,
                    "graph_count": graph_count,
                    "soil_location":soil_location
                }

                return render(request, 'dashboard_page.dart', context) # embed_dashboard.html
            else:
                return JsonResponse({"success": False, "error": "Dashboard is not public"})
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")
    
# To view dashboard publicly
def sharedDashboard(request, channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            channel_privacy = channel.get('privacy', '')
            if channel_privacy == "public":
                print("Found channel")
                channel_name = channel.get('channel_name', '')
                description = channel.get('description', '')
                sensor = channel.get('sensor', '')
                API=""
                graph_count=0
                for datapoint in sensor:
                    if 'DHT_sensor' in datapoint:
                        dht = datapoint['DHT_sensor']
                        db_humid_temp, collection_humid_temp = connect_to_mongodb('sensor', 'DHT11')
                        dht_id = ObjectId(dht)
                        humid_temp_data = collection_humid_temp.find_one({"_id": dht_id})
                        API=humid_temp_data.get("API_KEY",'')
                        graph_count+=2
                    if 'PH_sensor' in datapoint:
                        ph = datapoint['PH_sensor']
                        db_ph, collection_ph = connect_to_mongodb('sensor', 'PHSensor')
                        ph_id = ObjectId(ph)
                        ph_data = collection_ph.find_one({"_id": ph_id})
                        API=ph_data.get("API_KEY",'')
                        graph_count+=1
                context = {
                    "channel_name": channel_name,
                    "description": description,
                    "channel_id": channel_id,
                    "API":API,
                    "graph_count":graph_count
                }

                return render(request, 'shared_dashboard.html', context) # shared_dashboard.html
            else:
                return JsonResponse({"success": False, "error": "Dashboard is not public"})
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# DECLARE PLANTFEED URL HERE
PLANTFEED_SHARING_URL="https://5e03-161-139-102-63.ngrok-free.app/"
PLANTFEED_SHARING_API_PATH=PLANTFEED_SHARING_URL+"group/PlantLink-Graph-API"

# To make channel to public and send API to Plantfeed - DONE
@csrf_exempt
def share_channel(request, channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link = PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES.get('userid', ''),
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/"
            }
            response = requests.post(plantfeed_link, json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success": " successfully sent to Plantfeed"}, status=200)
            else:
                return JsonResponse({"success": " successfully sent to Plantfeed"}, status=200)
                # return JsonResponse({"error": "Failed to share channel"}, status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"}, status=404)
    else:
        print("Error connecting to MongoDB.")
        return JsonResponse({"error": "Database connection error"}, status=500)
    
# TO SHARE PH CHART TO PLANTFEED - DONE
@csrf_exempt
def share_ph_chart(request, channel_id, start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    start_time = time.time()
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            print("found ph chart channel")
            plantfeed_link = PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES.get('userid', ''),
                "chart_type": "ph",
                "chart_name": chart_name,
                "start_date": start_date,
                "end_date": end_date,
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/phChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link, json=channel_data)
            if response.status_code == 200:
                end_time = time.time()
                print("Execution time: {:.2f} seconds".format(end_time - start_time))
                return JsonResponse({"success": "Chart successfully sent to Plantfeed"}, status=200)
            else:
                end_time = time.time()
                print("Execution time: {:.2f} seconds".format(end_time - start_time))
                return JsonResponse({"success": " successfully sent to Plantfeed"}, status=200)
                # return JsonResponse({"error": "Failed to share channel"}, status=500)
            

        else:
            return JsonResponse({"success": False, "error": "Document not found"}, status=404)
    else:
        print("Error connecting to MongoDB.")
        return JsonResponse({"success": False, "error": "Error connecting to MongoDB"}, status=500)

# TO SHARE HUMIDITY CHART TO PLANTFEED - DONE
@csrf_exempt
def share_humidity_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                # "userid": request.COOKIES.get('userid', ''),
                "userid": "4",
                "chart_type":"humidity",
                "chart_name": chart_name,
                "start_date": start_date,
                "end_date": end_date,
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/humidityChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE TEMPERATURE CHART TO PLANTFEED - DONE
@csrf_exempt 
def share_temperature_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES['userid'],
                "chart_type":"temperature",
                "start_date":start_date,
                "end_date":end_date,
                "chart_name":chart_name,
                # "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/662e17d552a86a39e8091cc2/humidityChart/2024-03-05/2024-06-18/"
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/temperatureChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE RAINFALL CHART TO PLANTFEED - DONE
@csrf_exempt 
def share_rainfall_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES['userid'],
                "chart_type":"rainfall",
                "start_date":{start_date},
                "end_date":{end_date},
                "chart_name":{chart_name},
                # "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/662e17d552a86a39e8091cc2/humidityChart/2024-03-05/2024-06-18/"
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/rainfallChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE NITROGEN CHART TO PLANTFEED - DONE
@csrf_exempt 
def share_nitrogen_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES['userid'],
                "chart_type":"nitrogen",
                "start_date":start_date,
                "end_date":end_date,
                "chart_name":chart_name,
                # "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/662e17d552a86a39e8091cc2/humidityChart/2024-03-05/2024-06-18/"
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/nitrogenChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE phosphorous CHART TO PLANTFEED - DONE
@csrf_exempt 
def share_phosphorous_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,,
                "userid": request.COOKIES['userid'],
                "chart_type":"phosphorous",
                "start_date":start_date,
                "end_date":end_date,
                "chart_name":chart_name,
                # "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/662e17d552a86a39e8091cc2/humidityChart/2024-03-05/2024-06-18/"
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/phosphorousChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE POTASSIUM CHART TO PLANTFEED - DONE
@csrf_exempt 
def share_potassium_chart(request,channel_id,start_date, end_date, chart_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            plantfeed_link=PLANTFEED_SHARING_API_PATH
            channel_data = {
                "channel_id": "4",
                    # "channel_id": _id,
                "userid": request.COOKIES['userid'],
                "chart_type":"potassium",
                "start_date":start_date,
                "end_date":end_date,
                "chart_name":chart_name,
                # "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/662e17d552a86a39e8091cc2/humidityChart/2024-03-05/2024-06-18/"
                "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/potassiumChart/{start_date}/{end_date}/"
            }
            response = requests.post(plantfeed_link,json=channel_data)
            if response.status_code == 200:
                return JsonResponse({"success":"Chart successfuly send to Plantfeed"},status=200)
            else:
                return JsonResponse({"error":"Failed to share channel"},status=500)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO SHARE CROP SUGGESTION TO PLANTFEED
@csrf_exempt
def share_crop_table(request, channel_id, start_date, end_date, table_name):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            result = collection.update_one(
                {"_id": _id},
                {"$set": {"privacy": "public"}}
            )
            if result.modified_count > 0:
                plantfeed_link = PLANTFEED_SHARING_API_PATH
                table_data = {
                    "channel_id": "4",
                    # "channel_id": _id,
                    "userid": request.COOKIES['userid'],
                    "table_name": table_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "embed_link": f"https://shiroooo.pythonanywhere.com/mychannel/embed/channel/{channel_id}/cropTable/{start_date}/{end_date}/"
                }
                response = requests.post(plantfeed_link, json=table_data)
                if response.status_code == 200:
                    return JsonResponse({"success": "Table successfully sent to PlantFeed"}, status=200)
                else:
                    return JsonResponse({"success": " successfully sent to Plantfeed"}, status=200)
                    # return JsonResponse({"error": "Failed to share table"}, status=500)
        else:
            return JsonResponse({"success": " successfully sent to Plantfeed"}, status=200)
            # return JsonResponse({"error": "Channel not found"}, status=404)
    else:
        return JsonResponse({"error": "Error connecting to MongoDB"}, status=500)

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


def getSharedDashboardDetail(request,channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            print("Found channel")
            channel_name = channel.get('channel_name', '')
            description = channel.get('description', '')
            sensor = channel.get('sensor', '')

            ph_values = []
            timestamps = []
            humid_values = []
            temp_values = []
            timestamps_humid_temp = []
            API=""
            graph_count=0
            for datapoint in sensor:
                if 'DHT_sensor' in datapoint:
                    dht = datapoint['DHT_sensor']
                    db_humid_temp, collection_humid_temp = connect_to_mongodb('sensor', 'DHT11')
                    dht_id = ObjectId(dht)
                    humid_temp_data = collection_humid_temp.find_one({"_id": dht_id})
                    API=humid_temp_data.get("API_KEY",'')
                    graph_count+=2
                    for data_point in humid_temp_data.get('sensor_data', []):
                        humidity_value = data_point.get('humidity_value', '')
                        temperature_value = data_point.get('temperature_value', '')

                        # Append humidity value and temperature value to lists
                        humid_values.append(humidity_value)
                        temp_values.append(temperature_value)

                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        timestamps_humid_temp.append(formatted_timestamp)
                if 'PH_sensor' in datapoint:
                    ph = datapoint['PH_sensor']
                    db_ph, collection_ph = connect_to_mongodb('sensor', 'PHSensor')
                    ph_id = ObjectId(ph)
                    ph_data = collection_ph.find_one({"_id": ph_id})
                    API=ph_data.get("API_KEY",'')
                    graph_count+=1
                    if ph_data:
                        for data_point in ph_data.get('sensor_data', []):
                            ph_values.append(data_point.get('ph_value', ''))
                            timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                            formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                            timestamps.append(formatted_timestamp)
                    else:
                        print("No PH sensor data found for the given ID")
            context = {
                "channel_name": channel_name,
                "description": description,
                "channel_id": channel_id,
                "ph_values": ph_values,
                "timestamps": timestamps,
                "humid_values": humid_values,
                "temp_values": temp_values,
                "timestamps_humid_temp": timestamps_humid_temp,
                "API":API,
                "graph_count":graph_count
            }

            print("before model")
            # Load the trained Random Forest model
            model = load_trained_model()

            if model:
                # Prepare input data for model prediction
                input_data = {
                    'N': 0,  # Provide dummy values for features not used in prediction
                    'P': 0,
                    'K': 0,
                    'temperature': float(temp_values[-1]) if temp_values else 0.0,  # Example temperature value
                    'humidity': float(humid_values[-1]) if humid_values else 0.0,  # Example humidity value
                    'ph': float(ph_values[-1]) if ph_values else 0.0,  # Example pH value
                    'rainfall': 120.0,  # Example rainfall value
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

# ADD SENSOR - DONE
@csrf_exempt
def add_sensor(request, channel_id):
    if request.method == 'POST':
        channel_id = channel_id
        API_KEY = request.POST.get('apiKey')
        db_channel, collection_channel = connect_to_mongodb('Channel', 'dashboard')
        _id=ObjectId(channel_id)
        filter_criteria = {'_id': _id}
        update_result = collection_channel.update_one(filter_criteria, {'$set': {'API_KEY': API_KEY}})
        update_result2 = collection_channel.update_one(filter_criteria, {'$set': {'allow_API': "permit"}})
        if update_result.modified_count >0:
            print("success add sensor")
            return redirect('view_channel_sensor', channel_id=channel_id)
        else:
            print("fail add sensor")
    else:
        _id = ObjectId(channel_id)
        db, collection = connect_to_mongodb('Channel', 'dashboard')

        if db is not None and collection is not None:
            channel = collection.find_one({"_id": _id})
            if channel:
                print("Found channel")
                sensor_api = channel.get('API_KEY', '')
                if sensor_api:
                    context = {"channel_id": channel_id,"API_KEY":sensor_api}
                    return render(request, 'add_sensor.html', context)
                else:
                    context = {"channel_id": channel_id}
                    return render(request, 'add_sensor.html', context)

# MANAGE SENSOR BASED ON API KEY - DONE
def manage_sensor(request, channel_id):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')

    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})
        if channel:
            print("Found channel")
            sensor_api = channel.get('API_KEY', '')
            sensor_list = []

            if not sensor_api:
                return JsonResponse({"error": "No API key set for this channel"}, status=400)
            else:
                # Fetch data from different sensor collections
                sensors = [
                    {"name": "DHT11", "db_name": "DHT11"},
                    {"name": "PHSensor", "db_name": "PHSensor"},
                    {"name": "NPK", "db_name": "NPK"},
                    {"name": "Rainfall", "db_name": "rainfall"}
                ]

                for sensor in sensors:
                    sensor_db, sensor_collection = connect_to_mongodb('sensor', sensor['db_name'])
                    if sensor_db is not None and sensor_collection is not None:
                        sensor_data = sensor_collection.find_one({"API_KEY": sensor_api})
                        if sensor_data:
                            sensor_list.append({
                                "sensor_id": str(sensor_data.get('_id')),
                                "sensor_name": sensor_data.get('sensor_name'),
                                "sensor_type": sensor_data.get('sensor_type'),
                                "sensor_data_count": len(sensor_data.get('sensor_data', []))
                            })

            return JsonResponse({
                "channel_id": channel_id,
                "sensors": sensor_list,
                "API_KEY_VALUE": sensor_api
            })

    return JsonResponse({"error": "Channel not found"}, status=404)

#   DELETE SENSOR - DONE
@csrf_exempt
def delete_sensor(request, channel_id, sensor_type):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    print(sensor_type)
    if db is not None and collection is not None:
        channel = collection.find_one({'_id': _id})
        if channel:
            api_key = channel.get('API_KEY', '')
            if api_key:
                if sensor_type == "DHT11":
                    dht_db, dht_collection = connect_to_mongodb('sensor', 'DHT11')
                    delete_action = dht_collection.find_one({"API_KEY": api_key})
                    if delete_action:
                        dht_collection.delete_one({"API_KEY": api_key})
                        return redirect('view_channel_sensor', channel_id=channel_id)
                    else:
                        return JsonResponse({"success": False, "error": "DHT11 sensor document not found."}, status=404)
                elif sensor_type == "NPK":
                    NPK_db, NPK_collection = connect_to_mongodb('sensor', 'NPK')
                    delete_action = NPK_collection.find_one({"API_KEY": api_key})
                    if delete_action:
                        NPK_collection.delete_one({"API_KEY": api_key})
                        return redirect('view_channel_sensor', channel_id=channel_id)
                    else:
                        return JsonResponse({"success": False, "error": "NPKSensor document not found."}, status=404)
                elif sensor_type == "ph_sensor":
                    ph_db, ph_collection = connect_to_mongodb('sensor', 'PHSensor')
                    delete_action = ph_collection.find_one({"API_KEY": api_key})
                    if delete_action:
                        ph_collection.delete_one({"API_KEY": api_key})
                        return redirect('view_channel_sensor', channel_id=channel_id)
                    else:
                        return JsonResponse({"success": False, "error": "PHSensor document not found."}, status=404)
                elif sensor_type == "rainfall":
                    rainfall_db, rainfall_collection = connect_to_mongodb('sensor', 'rainfall')
                    delete_action = rainfall_collection.find_one({"API_KEY": api_key})
                    if delete_action:
                        rainfall_collection.delete_one({"API_KEY": api_key})
                        return redirect('view_channel_sensor', channel_id=channel_id)
                    else:
                        return JsonResponse({"success": False, "error": "rainfall document not found."}, status=404)
                else:
                    return JsonResponse({"success": False, "error": "Invalid sensor type."}, status=400)
            else:
                return JsonResponse({"success": False, "error": "API_KEY not set for this channel."}, status=400)
        else:
            return JsonResponse({"success": False, "error": "Channel document not found."}, status=404)
    else:
        return JsonResponse({"error": "Database connection error"}, status=500)

# EDIT SENSOR - DONE (changed)
@csrf_exempt
def edit_sensor(request, sensor_type, sensor_id, channel_id):
    if request.method == 'POST':
        print(sensor_type)
        # Fetch form data
        sensor_name = request.POST.get('sensorName')
        sensor_type = request.POST.get('sensorType')
        API_KEY = request.POST.get('ApiKey')

        if sensor_type == "DHT11":
            db, collection = connect_to_mongodb('sensor', 'DHT11')
            if db is not None and collection is not None:
                # Convert channel_id to ObjectId
                _id = ObjectId(sensor_id)
                result = collection.update_one(
                    {"_id": _id},
                    {"$set": {
                        "sensor_name": sensor_name,
                    }}
                )
                if result.modified_count > 0:
                    # Channel updated successfully
                    return redirect('manage_sensor', channel_id=channel_id)
                else:
                    return redirect('view_channel_sensor', channel_id=channel_id)

        elif sensor_type == "ph_sensor":
            db, collection = connect_to_mongodb('sensor', 'PHSensor')
            if db is not None and collection is not None:
                # Convert channel_id to ObjectId
                _id = ObjectId(sensor_id)
                result = collection.update_one(
                    {"_id": _id},
                    {"$set": {
                        "sensor_name": sensor_name,
                    }}
                )
                if result.modified_count > 0:
                    # Channel updated successfully
                    return redirect('manage_sensor', channel_id=channel_id)
                else:
                    return redirect('view_channel_sensor', channel_id=channel_id)
        elif sensor_type == "NPK":
            db, collection = connect_to_mongodb('sensor', 'NPK')
            if db is not None and collection is not None:
                # Convert channel_id to ObjectId
                _id = ObjectId(sensor_id)
                result = collection.update_one(
                    {"_id": _id},
                    {"$set": {
                        "sensor_name": sensor_name,
                    }}
                )
                if result.modified_count > 0:
                    # Channel updated successfully
                    return redirect('manage_sensor', channel_id=channel_id)
                else:
                    return redirect('view_channel_sensor', channel_id=channel_id)
        elif sensor_type == "rainfall":
            db, collection = connect_to_mongodb('sensor', 'rainfall')
            if db is not None and collection is not None:
                # Convert channel_id to ObjectId
                _id = ObjectId(sensor_id)
                result = collection.update_one(
                    {"_id": _id},
                    {"$set": {
                        "sensor_name": sensor_name,
                    }}
                )
                if result.modified_count > 0:
                    # Channel updated successfully
                    return redirect('manage_sensor', channel_id=channel_id)
                else:
                    return redirect('view_channel_sensor', channel_id=channel_id)

    else:
        # Fetch channel details from MongoDB to pre-fill the form
        if sensor_type == "DHT11":
            db, collection = connect_to_mongodb('sensor', 'DHT11')
            _id = ObjectId(sensor_id)
            sensor = collection.find_one({"_id": _id})
            if sensor:
                sensor_name = sensor.get("sensor_name", "")
                API_KEY = sensor.get("API_KEY", '')
                context = {
                    "channel_id": channel_id,
                    "sensor_name": sensor_name,
                    "sensor_type": sensor_type,
                    "API_KEY": API_KEY,
                }
                # Render the edit form with channel data
                return render(request, 'edit_sensor.html', context)
            else:
                # Handle if channel not found in MongoDB
                return JsonResponse({"success": False, "error": "Channel not found"})
        elif sensor_type == "ph_sensor":
            db, collection = connect_to_mongodb('sensor', 'PHSensor')
            _id = ObjectId(sensor_id)
            sensor = collection.find_one({"_id": _id})
            if sensor:
                sensor_name = sensor.get("sensor_name", "")
                API_KEY = sensor.get("API_KEY", '')
                context = {
                    "channel_id": channel_id,
                    "sensor_name": sensor_name,
                    "sensor_type": sensor_type,
                    "API_KEY": API_KEY,
                }
                # Render the edit form with channel data
                return render(request, 'edit_sensor.html', context)
            else:
                # Handle if channel not found in MongoDB
                return JsonResponse({"success": False, "error": "Channel not found"})

    # Default response if request method is not 'POST'
    return JsonResponse({"success": False, "error": "Invalid request method"})

# For retrieve Humidity and Temperature data - DONE
def getHumidityTemperatureData(request, channel_id, start_date, end_date):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            sensor = channel.get('sensor', '')
            humid_values = []
            temp_values = []
            timestamps_humid_temp = []
            API = channel.get('API_KEY', '')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Fetch data from sensor:DHT11
            db_humid_temp, collection_humid_temp = connect_to_mongodb('sensor', 'DHT11')
            if db_humid_temp is not None and collection_humid_temp is not None:
                humid_temp_data = collection_humid_temp.find_one({"API_KEY": API})
                if humid_temp_data:
                    for data_point in humid_temp_data.get('sensor_data', []):
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        if start_date <= timestamp_obj <= end_date:
                            humidity_value = data_point.get('humidity_value', '')
                            temperature_value = data_point.get('temperature_value', '')
                            humid_values.append(humidity_value)
                            temp_values.append(temperature_value)
                            formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                            timestamps_humid_temp.append(formatted_timestamp)
            context = {
                "channel_id": channel_id,
                "humid_values": humid_values,
                "temp_values": temp_values,
                "timestamps_humid_temp": timestamps_humid_temp,
                "API": API,
            }
            print("check here",context)
            return JsonResponse(context)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# For retrieve NPK data - DONE
def getNPKData(request, channel_id, start_date, end_date):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            sensor = channel.get('sensor', '')
            nitrogen_values = []
            phosphorous_values = []
            potassium_values = []
            timestamps_NPK = []
            API = channel.get('API_KEY', '')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Fetch data from sensor:DHT11
            db_NPK, collection_NPK = connect_to_mongodb('sensor', 'NPK')
            if db_NPK is not None and collection_NPK is not None:
                NPK_data = collection_NPK.find_one({"API_KEY": API})
                if NPK_data:
                    for data_point in NPK_data.get('sensor_data', []):
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        if start_date <= timestamp_obj <= end_date:
                            nitrogen_value = data_point.get('nitrogen_value', '')
                            phosphorous_value = data_point.get('phosphorous_value', '')
                            potassium_value = data_point.get('potassium_value', '')
                            nitrogen_values.append(nitrogen_value)
                            phosphorous_values.append(phosphorous_value)
                            potassium_values.append(potassium_value)
                            formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                            timestamps_NPK.append(formatted_timestamp)
                        else:
                            print("invalid timestamp")
                else:
                    print("npk_data empty")
            context = {
                "channel_id": channel_id,
                "nitrogen_values" :nitrogen_values,
                "phosphorous_values" :phosphorous_values, 
                "potassium_values" :potassium_values, 
                "timestamps_NPK" :timestamps_NPK, 
                "API": API,
            }
            return JsonResponse(context)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# For retrieve PH data - DONE
def getPHData(request, channel_id, start_date, end_date):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            sensor = channel.get('sensor', '')
            ph_values = []
            timestamps = []
            API = channel.get('API_KEY', '')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            db_ph, collection_ph = connect_to_mongodb('sensor', 'PHSensor')
            if db_ph is not None and collection_ph is not None:
                ph_data = collection_ph.find_one({"API_KEY": API})
                if ph_data:
                    for data_point in ph_data.get('sensor_data', []):
                        ph_values.append(data_point.get('ph_value', ''))
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        timestamps.append(formatted_timestamp)

            context = {
                "channel_id": channel_id,
                "ph_values": ph_values,
                "timestamps": timestamps,
                "API": API,
            }
            return JsonResponse(context)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# For retrieve rainfall data - DONE
def getRainfallData(request, channel_id, start_date, end_date):
    _id = ObjectId(channel_id)
    db, collection = connect_to_mongodb('Channel', 'dashboard')
    if db is not None and collection is not None:
        channel = collection.find_one({"_id": _id})

        if channel:
            sensor = channel.get('sensor', '')
            rainfall_values = []
            rainfall_timestamps = []
            API = channel.get('API_KEY', '')
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

            db_rainfall, collection_rainfall = connect_to_mongodb('sensor', 'rainfall')
            if db_rainfall is not None and collection_rainfall is not None:
                rainfall_data = collection_rainfall.find_one({"API_KEY": API})
                if rainfall_data:
                    for data_point in rainfall_data.get('sensor_data', []):
                        rainfall_values.append(data_point.get('rainfall_value', ''))
                        timestamp_obj = data_point.get('timestamp', datetime.utcnow())
                        formatted_timestamp = timestamp_obj.astimezone(pytz.utc).strftime('%d-%m-%Y')
                        rainfall_timestamps.append(formatted_timestamp)

            context = {
                "channel_id": channel_id,
                "rainfall_values": rainfall_values,
                "timestamps": rainfall_timestamps,
                "API": API,
            }
            return JsonResponse(context)
        else:
            return JsonResponse({"success": False, "error": "Document not found"})
    else:
        print("Error connecting to MongoDB.")

# TO CHANGE CHANNEL PERMISSION TO FORBID API - DONE
@csrf_exempt
def forbid_API(request, channel_id):
    if request.method == 'POST':
        db, collection = connect_to_mongodb('Channel', 'dashboard')
        _id = ObjectId(channel_id)
        filter_criteria = {'_id': _id}
        update_result = collection.update_one(filter_criteria, {'$set': {'allow_API': 'not permitted'}})
        if update_result.modified_count > 0:
            return JsonResponse({'message': 'API access forbidden successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Failed to update API access'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

# TO CHANGE CHANNEL PERMISSION TO ALLOW API - DONE
@csrf_exempt
def permit_API(request, channel_id):
    if request.method == 'POST':
        db, collection = connect_to_mongodb('Channel', 'dashboard')
        _id = ObjectId(channel_id)
        filter_criteria = {'_id': _id}
        update_result = collection.update_one(filter_criteria, {'$set': {'allow_API': 'permit'}})
        if update_result.modified_count > 0:
            return JsonResponse({'message': 'API access permitted successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Failed to update API access'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
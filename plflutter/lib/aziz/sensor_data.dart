import 'dart:convert';
import 'package:http/http.dart' as http;


Future<List<SensorData>> fetchSensorData() async {
  final response = await http.get(Uri.parse('http://10.0.2.2:8000/mychannel/672484a397fae572346fda56/get_dashboard_data/'));

  if (response.statusCode == 200) {
    // Parse the response as a Map
    final Map<String, dynamic> data = json.decode(response.body);

    List<SensorData> sensorDataList = [];

    // Extracting and adding pH data
    if (data['ph_values'] != null) {
      for (var i = 0; i < data['ph_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'PH',
          value: double.parse(data['ph_values'][i]),
          timestamp: data['timestamps'][i],
        ));
      }
    }

    // Extracting and adding Humidity data
    if (data['humid_values'] != null) {
      for (var i = 0; i < data['humid_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'Humidity',
          value: double.parse(data['humid_values'][i]),
          timestamp: data['timestamps_humid_temp'][i],
        ));
      }
    }

    // Extracting and adding Temperature data
    if (data['temp_values'] != null) {
      for (var i = 0; i < data['temp_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'Temperature',
          value: double.parse(data['temp_values'][i]),
          timestamp: data['timestamps_humid_temp'][i],
        ));
      }
    }

    // Extracting and adding Nitrogen data
    if (data['nitrogen_values'] != null) {
      for (var i = 0; i < data['nitrogen_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'Nitrogen',
          value: double.parse(data['nitrogen_values'][i]),
          timestamp: data['timestamps_NPK'][i],
        ));
      }
    }

    // Extracting and adding Phosphorous data
    if (data['phosphorous_values'] != null) {
      for (var i = 0; i < data['phosphorous_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'Phosphorous',
          value: double.parse(data['phosphorous_values'][i]),
          timestamp: data['timestamps_NPK'][i],
        ));
      }
    }

    // Extracting and adding Potassium data
    if (data['potassium_values'] != null) {
      for (var i = 0; i < data['potassium_values'].length; i++) {
        sensorDataList.add(SensorData(
          sensorType: 'Potassium',
          value: double.parse(data['potassium_values'][i]),
          timestamp: data['timestamps_NPK'][i],
        ));
      }
    }

    return sensorDataList;
  } else {
    throw Exception('Failed to load sensor data');
  }
}

class SensorData {
  final String sensorType;
  final double value;
  final String timestamp;

  SensorData({required this.sensorType, required this.value, required this.timestamp});

  factory SensorData.fromJson(Map<String, dynamic> json) {
    return SensorData(
      sensorType: json['sensor_type'],
      value: json['value'],
      timestamp: json['timestamp'],
    );
  }
}


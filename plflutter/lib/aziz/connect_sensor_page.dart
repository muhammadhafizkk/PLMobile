import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dashboard_page.dart';

class AddSensorScreen extends StatelessWidget {
  final String channelId;
  //final String apiUrl;

  const AddSensorScreen({Key? key, required this.channelId}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final TextEditingController apiKeyController = TextEditingController();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Sensor'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Add new sensor to this channel',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 20),
              TextFormField(
                controller: apiKeyController,
                decoration: const InputDecoration(
                  labelText: 'API Key',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  ElevatedButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => DashboardScreen(channelId: channelId),
                        ),
                      ); // Close the modal
                    },
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.grey),
                    child: const Text('Close'),
                  ),
                  ElevatedButton(
                    onPressed: () {
                      _connectSensor(context, apiKeyController.text);
                    },
                    style: ElevatedButton.styleFrom(backgroundColor: Colors.blue),
                    child: const Text('Connect sensor'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _connectSensor(BuildContext context, String apiKey) async {
    if (apiKey.isEmpty) {
      _showSnackbar(context, "API Key cannot be empty");
      return;
    }

    final url = Uri.parse('http://127.0.0.1:8000/mychannel/$channelId/add_sensor'); 
    final response = await http.post(
      url,
      body: {'apiKey': apiKey},
    );

    if (response.statusCode == 200 || response.statusCode == 302) {
      final responseData = json.decode(response.body);
      if (responseData['success'] == true || response.reasonPhrase?.compareTo("Found") == 0) {
        _showSnackbar(context, "Sensor connected successfully!");
        Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => DashboardScreen(channelId: channelId),
                        ),
                      ); // Close the modal
      } else {
        _showSnackbar(context, "Failed to connect sensor.");
      }
    } else {
      _showSnackbar(context, "Error: ${response.reasonPhrase}");
    }
  }

  void _showSnackbar(BuildContext context, String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }
}

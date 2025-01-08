import 'package:flutter/material.dart';
//import 'manage_sensor_page.dart';
import 'package:plflutter/aziz/sensor_service.dart';
import 'package:plflutter/aziz/dashboard_page.dart';

class ConfigureSensorPage extends StatefulWidget {
  final String channelId;

  const ConfigureSensorPage({Key? key, required this.channelId}) : super(key: key);

  @override
  State<ConfigureSensorPage> createState() => _ConfigureSensorPageState();
}

class _ConfigureSensorPageState extends State<ConfigureSensorPage> {
  late Future<Map<String, dynamic>> _sensorData;

  @override
  void initState() {
    super.initState();
    _sensorData = SensorService().fetchSensors(widget.channelId);
  }

  // Edit sensor name action
  void _editSensorName(String sensorId, String currentName, String sensorType, String apiKey) {
    TextEditingController controller = TextEditingController(text: currentName);

    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Edit Sensor Name'),
          content: TextField(
            controller: controller,
            decoration: const InputDecoration(labelText: 'Sensor Name'),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
              },
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () async {
                final newName = controller.text;
                try {
                  await SensorService().editSensor(
                    channelId: widget.channelId,
                    sensorType: sensorType,
                    sensorId: sensorId,
                    newSensorName: newName,
                    apiKey: apiKey,
                  );
                  setState(() {
                    _sensorData = SensorService().fetchSensors(widget.channelId);
                  });
                  Navigator.pop(context); // Close dialog 
                  // Navigate to the ConfigureSensorPage (refresh new data)
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => ConfigureSensorPage(channelId: widget.channelId),
                    ),
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Sensor name updated successfully')),
                  );
                } catch (e) {
                  print('Error updating sensor: $e');
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Failed to update sensor name')),
                  );
                }
              },
              child: const Text('Save'),
            ),
          ],
        );
      },
    );
  }

  // Delete sensor action
  void _deleteSensor(String sensorId, String sensorType) {
    showDialog(
      context: context,
      builder: (context) {
        return AlertDialog(
          title: const Text('Delete Sensor'),
          content: const Text('Are you sure you want to delete this sensor?'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
              },
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () async {
                try {
                  await SensorService().deleteSensor(
                    channelId: widget.channelId,
                    sensorType: sensorType,
                  );
                  setState(() {
                    _sensorData = SensorService().fetchSensors(widget.channelId);
                  });
                  Navigator.pop(context); // Close dialog
                  // Navigate to the DashboardScreen
                  Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(
                      builder: (context) => DashboardScreen(channelId: widget.channelId),
                    ),
                  );
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Sensor deleted successfully')),
                  );
                } catch (e) {
                  print('Error deleting sensor: $e');
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Failed to delete sensor')),
                  );
                }
              },
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configure Sensors'),
      ),
      body: FutureBuilder<Map<String, dynamic>>(
        future: _sensorData,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!['sensors'].isEmpty) {
            return const Center(child: Text('No sensors found.'));
          } else {
            final apiKey = snapshot.data!['API_KEY_VALUE'];
            final sensors = snapshot.data!['sensors'];

            return Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Display API Key
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Text(
                    'API Key: $apiKey',
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
                const Divider(),

                // Display Sensor List
                Expanded(
                  child: ListView.builder(
                    itemCount: sensors.length,
                    itemBuilder: (context, index) {
                      final sensor = sensors[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                        child: ListTile(
                          title: Text( (sensor['sensor_name'] != null)
                              ? sensor['sensor_name']
                              : 'Unnamed Sensor'),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Type: ${sensor['sensor_type']}'),
                              Text('Data Count: ${sensor['sensor_data_count']}'),
                            ],
                          ),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.edit, color: Colors.blue),
                                onPressed: () => _editSensorName(
                                  sensor['sensor_id'],
                                  sensor['sensor_name'],
                                  sensor['sensor_type'],
                                  apiKey,
                                ),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete, color: Colors.red),
                                onPressed: () => _deleteSensor(
                                  sensor['sensor_id'], 
                                  sensor['sensor_type']
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            );
          }
        },
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:intl/intl.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:plflutter/aziz/dashboard_functions.dart';
import 'package:plflutter/aziz/connect_sensor_page.dart';
import 'package:plflutter/aziz/configure_sensor_page.dart';

class DashboardScreen extends StatefulWidget {
  
  final String channelId;
  const DashboardScreen({super.key, required this.channelId});
  
  //const DashboardScreen({super.key});

  @override
  _DashboardScreenState createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  late String channelId = widget.channelId;
  // Data lists for each sensor type
  List<double> phData = [];
  List<double> rainfallData = [];
  List<double> humidityData = [];
  List<double> tempData = [];
  List<double> nitrogenData = [];
  List<double> phosphorousData = [];
  List<double> potassiumData = [];

  // Timestamps for each sensor type
  List<String> phTimestamps = [];
  List<String> rainfallTimestamps = [];
  List<String> humidTempTimestamps = [];
  List<String> npkTimestamps = [];

  bool isLoading = true;

  // Default chart type for each chart section
  Map<String, String> selectedChartTypes = {
    "pH Level Chart": "Spline Chart",
    "Rainfall Chart": "Spline Chart",
    "Humidity Chart": "Spline Chart",
    "Temperature Chart": "Spline Chart",
    "Nitrogen Chart": "Spline Chart",
    "Phosphorous Chart": "Spline Chart",
    "Potassium Chart": "Spline Chart",
  };

  @override
  void initState() {
    super.initState();
    fetchSensorData();
  }

  Future<void> fetchSensorData() async {
    try {
      final response = await http.get(
        Uri.parse('http://10.0.2.2:8000/mychannel/$channelId/get_dashboard_data/')
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        setState(() {
          // Safely parse data and provide defaults for null or invalid fields
          phData = List<double>.from(
            (data['ph_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          rainfallData = List<double>.from(
            (data['rainfall_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          humidityData = List<double>.from(
            (data['humid_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          tempData = List<double>.from(
            (data['temp_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          nitrogenData = List<double>.from(
            (data['nitrogen_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          phosphorousData = List<double>.from(
            (data['phosphorous_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );
          potassiumData = List<double>.from(
            (data['potassium_values'] as List?)?.map((v) => double.tryParse(v.toString()) ?? 0.0) ?? []
          );

          phTimestamps = List<String>.from(data['timestamps'] ?? []);
          rainfallTimestamps = List<String>.from(data['rainfall_timestamps'] ?? []);
          humidTempTimestamps = List<String>.from(data['timestamps_humid_temp'] ?? []);
          npkTimestamps = List<String>.from(data['timestamps_NPK'] ?? []);

          isLoading = false;
        });
      } else {
        setState(() {
          isLoading = false;
        });
        debugPrint('Failed to load sensor data. Status Code: ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      debugPrint('Error fetching data: $e');
    }
  }

  // Generate FlSpots for each sensor type
  List<FlSpot> _generateSpots(List<double> data) {
    return List.generate(data.length, (index) {
      return FlSpot(index.toDouble(), data[index]);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Dashboard")),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              child: Column(
                children: [
                  _buildChartSection("pH Level Chart", _generateSpots(phData), phTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Rainfall Chart", _generateSpots(rainfallData), rainfallTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Humidity Chart", _generateSpots(humidityData), humidTempTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Temperature Chart", _generateSpots(tempData), humidTempTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Nitrogen Chart", _generateSpots(nitrogenData), npkTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Phosphorous Chart", _generateSpots(phosphorousData), npkTimestamps),
                  const SizedBox(height: 20),
                  _buildChartSection("Potassium Chart", _generateSpots(potassiumData), npkTimestamps),

                  const SizedBox(height: 15),
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Column(
                      children: [
                        const SizedBox(width: 10),
                        GreenButtonWithIcon(
                          label: 'Configure Sensor',
                          onPressed: () {
                            Navigator.push(
                              context, 
                              MaterialPageRoute(
                                builder: (context) => ConfigureSensorPage(channelId: channelId)
                                )
                              );
                          },
                        ),
                        const SizedBox(width: 10),
                        GreenButtonWithIcon(
                          label: 'Connect Sensor',
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => AddSensorScreen(channelId: channelId)
                              ),
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildChartSection(String title, List<FlSpot> spots, List<String> timestamps) {

  String chartDataType="";
  if (title=="pH Level Chart"){chartDataType="phChart";}
  else if (title=="Rainfall Chart"){chartDataType="rainfallChart";}
  else if (title=="Humidity Chart"){chartDataType="humidityChart";}
  else if (title=="Temperature Chart"){chartDataType="temperatureChart";}
  else if (title=="Nitrogen Chart"){chartDataType="nitrogenChart";}
  else if (title=="Phosphorous Chart"){chartDataType="phosphorousChart";}
  else if (title=="Potassium Chart"){chartDataType="potassiumChart";}

  if (spots.isEmpty) {
    return Column(
      children: [
        Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 10),
        const Text("No data available", style: TextStyle(color: Colors.grey)),
      ],
    );
  }

  double minXValue = spots.first.x;
  double maxXValue = spots.last.x;

  double minYValue = spots.map((spot) => spot.y).reduce((a, b) => a < b ? a : b);
  double maxYValue = spots.map((spot) => spot.y).reduce((a, b) => a > b ? a : b);

  return Column(
    children: [
      Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title),
          DropdownButton<String>(
            value: selectedChartTypes[title],
            items: ["Spline Chart", "Line Chart", "Bar Chart"]
                .map((type) => DropdownMenuItem(value: type, child: Text(type)))
                .toList(),
            onChanged: (value) {
              setState(() {
                selectedChartTypes[title] = value!;
              });
            },
          ),
        ],
      ),
      SizedBox(
        height: 300,
        child: LineChart(
          LineChartData(
            minX: minXValue,
            maxX: maxXValue,
            minY: minYValue,
            maxY: maxYValue,
            lineBarsData: [
              _getChartData(spots, selectedChartTypes[title].toString()),
            ],
          ),
        ),
      ),
      const SizedBox(height: 10),
      TextButton.icon(
        onPressed: () async {
          if (timestamps.isEmpty) {
            _showErrorDialog("Timestamps are required to share the chart.");
            return;
          }

          String startDate = timestamps.first;
          String endDate = timestamps.last;
          String chartType = selectedChartTypes[title] ?? "Spline Chart";

          await shareChart(title, spots, chartDataType, startDate, endDate, chartType);
        },
        icon: const Icon(Icons.share),
        label: const Text("Share Chart"),
        style: TextButton.styleFrom(
          foregroundColor: Colors.white,
          backgroundColor: Colors.green,
        ),
      ),
    ],
  );
}


  LineChartBarData _getChartData(List<FlSpot> spots, String chartType) {
    switch (chartType) {
      case "Line Chart":
        return LineChartBarData(
          spots: spots,
          isCurved: false, // Line chart is not curved
          color: Colors.blue,
          belowBarData: BarAreaData(show: false),
        );
      case "Bar Chart":
        return LineChartBarData(
          spots: spots,
          isCurved: false,
          barWidth: 8,
          color: Colors.green,
          dotData: const FlDotData(show: false),
          belowBarData: BarAreaData(show: false),
        );
      default: // "Spline Chart"
        return LineChartBarData(
          spots: spots,
          isCurved: true, // Spline chart is curved
          color: const Color.fromARGB(255, 0, 244, 45),
          belowBarData: BarAreaData(show: false),
        );
    }
  }
  List<BarChartGroupData> _getBarChartData(List<FlSpot> spots) {
    return spots.map((spot) {
      return BarChartGroupData(
        x: spot.x.toInt(),
        barRods: [
          BarChartRodData(
            toY: spot.y,
            color: Colors.green,
            width: 8,
          ),
        ],
      );
    }).toList();
  }

  Future<void> shareChart(String chartTitle, List<FlSpot> spots, String chartDataType, String startDate, String endDate, String chartType) async {
  
  final DateTime startDateObj = DateFormat("dd-MM-yyyy").parse(startDate);
  final DateTime endDateObj = DateFormat("dd-MM-yyyy").parse(endDate);
  final String formattedStartDate = DateFormat("yyyy-MM-dd").format(startDateObj);
  final String formattedEndDate = DateFormat("yyyy-MM-dd").format(endDateObj);

  final url = 'http://10.0.2.2:8000/mychannel/$channelId/share_chart/$chartDataType/$formattedStartDate/$formattedEndDate/$chartTitle/';
  
  final payload = {
  "data_points": spots.map((spot) => {"x": spot.x, "y": spot.y}).toList(),
  };


  try {
    final response = await http.post(
      Uri.parse(url),
      headers: {
        'Content-Type': 'application/json',
      },
      body: jsonEncode(payload),
    );

    if (response.statusCode == 200) {
      final responseData = jsonDecode(response.body);
    if (responseData["success"] != null) {  // Changed this condition
      showDialog(
        context: context,
        builder: (context) {
          return AlertDialog(
            title: const Text("Chart Shared"),
            content: Text(responseData["success"]),  // Show the actual success message
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text("OK"),
              ),
            ],
          );
        },
      );
    } else {
    _showErrorDialog("Failed to share the chart.");
  }
    } else {
      _showErrorDialog("Error: ${response.statusCode}");
    }
  } catch (e) {
    debugPrint('Error sharing chart: $e');
    _showErrorDialog("An unexpected error occurred.");
  }
}


void _showErrorDialog(String message) {
  showDialog(
    context: context,
    builder: (context) {
      return AlertDialog(
        title: const Text("Error"),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text("OK"),
          ),
        ],
      );
    },
  );
}
}



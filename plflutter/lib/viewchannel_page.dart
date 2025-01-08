import 'package:flutter/material.dart';
import 'package:plflutter/deletechannel.dart';
import 'package:plflutter/editchannel_page.dart';
import 'package:plflutter/aziz/dashboard_page.dart';
import 'fetch_channel.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

class ViewChannel extends StatelessWidget {
  const ViewChannel({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('View Channel'),
        backgroundColor: Colors.green[300],
        centerTitle: true,
      ),
      body: const Column(
        children: [
          BasePage(),
          SizedBox(height: 20),
          Expanded(child: ChannelsList()),
        ],
      ),
    );
  }
}

class BasePage extends StatefulWidget {
  const BasePage({super.key});

  @override
  State<BasePage> createState() => _BasePageState();
}

class _BasePageState extends State<BasePage> {
  int totalChannels = 0;
  int totalSensors = 0;
  int publicChannels = 0;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    fetchChannelStatistics();
  }

  Future<void> fetchChannelStatistics() async {
    const String apiUrl = "http://10.0.2.2:8000/mychannel/stats/";
    try {
      final response = await http.get(Uri.parse(apiUrl));
      if (response.statusCode == 200) {
        final Map<String, dynamic> stats = json.decode(response.body);
        setState(() {
          totalChannels = stats['totalChannels'] ?? 0;
          totalSensors = stats['totalSensors'] ?? 0;
          publicChannels = stats['publicChannels'] ?? 0;
          isLoading = false;
        });
      } else {
        throw Exception("Failed to fetch statistics.");
      }
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error fetching stats: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          child: ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.blue[200],
            ),
            onPressed: () {
              Navigator.pushNamed(context, '/channels/create');
            },
            child: const Text('Create +'),
          ),
        ),
        Container(
          color: Colors.green[300],
          padding: const EdgeInsets.all(10),
          child: isLoading
              ? const Center(child: CircularProgressIndicator())
              : InfoCard(
                  totalChannels: totalChannels,
                  totalSensors: totalSensors,
                  publicChannels: publicChannels,
                ),
        ),
      ],
    );
  }
}

class InfoCard extends StatelessWidget {
  final int totalChannels;
  final int totalSensors;
  final int publicChannels;

  const InfoCard({
    super.key,
    required this.totalChannels,
    required this.totalSensors,
    required this.publicChannels,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          child: Row(
            children: [
              Image.asset('assets/plant1.png', width: 25),
              const Text(' '),
              const Text('Total Channels: '),
              Text(totalChannels.toString()),

              const Expanded(child: SizedBox()),

              Image.asset('assets/plant1.png', width: 25),
              const Text(' '),
              const Text('Registered Sensors: '),
              Text(totalSensors.toString()),
            ],
          ),
        ),
        Container(
          padding: const EdgeInsets.all(10),
          child: Row(
            children: [
              Image.asset('assets/plant1.png', width: 25),
              const Text(' '),
              const Text('Public Channels: '),
              Text(publicChannels.toString()),

              const Expanded(child: SizedBox()),
            ],
          ),
        ),
      ],
    );
  }
}

class ChannelsList extends StatefulWidget {
  const ChannelsList({super.key});

  @override
  State<ChannelsList> createState() => _ChannelsListState();
}

class _ChannelsListState extends State<ChannelsList> {
  List<Map<String, dynamic>> _allChannels = [];
  List<Map<String, dynamic>> _filteredChannels = [];
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadChannels();
  }

  Future<void> _loadChannels() async {
    setState(() {
      isLoading = true;
    });
    try {
      final channels = await ChannelService().fetchChannels();
      setState(() {
        _allChannels = channels;
        _filteredChannels = channels;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading channels: $e')),
      );
    }
  }

  void _filterChannels(String query) {
    setState(() {
      if (query.isEmpty) {
        _filteredChannels = _allChannels;
      } else {
        _filteredChannels = _allChannels
            .where((channel) =>
                channel['channel_name'] != null &&
                channel['channel_name']
                    .toLowerCase()
                    .contains(query.toLowerCase()))
            .toList();
      }
    });
  }

  Future<void> _navigateToPage(
      BuildContext context, String action, Map<String, dynamic> channel) async {
    if (action == "Edit") {
      final result = await Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => EditChannelPage(channel: channel),
        ),
      );
      if (result == true) {
        _loadChannels();
        
      }
    } else {
      // Navigate to the DashboardScreen for "View" action
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => DashboardScreen(channelId: channel['_id']),
        // builder: (context) => PlaceholderPage(action: action, channelName: channel['channel_name']),
      ),
    );
    }
  }

  void _showDeleteDialog(String channelId) {
    showDialog(
      context: context,
      builder: (context) {
        return DeleteChannelDialog(
          channelId: channelId,
          onDelete: _loadChannels,
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return isLoading
        ? const Center(child: CircularProgressIndicator())
        : Padding(
            padding: const EdgeInsets.all(8.0),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: TextField(
                    decoration: const InputDecoration(
                      labelText: "Search Channels",
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(),
                    ),
                    onChanged: _filterChannels,
                  ),
                ),
                Expanded(
                  child: _filteredChannels.isEmpty
                      ? const Center(child: Text("No channels found"))
                      : SingleChildScrollView(
                        scrollDirection: Axis.vertical,
                        child: PaginatedDataTable(
                            header: const Text("Channels"),
                            rowsPerPage: 6, // Set your rows per page
                            columns: const [
                              DataColumn(label: Text('Channel Name')),
                              DataColumn(label: Text('Description')),
                              DataColumn(label: Text('Date Created')),
                              DataColumn(label: Text('Date Modified')),
                              DataColumn(label: Text('Sensors')),
                              DataColumn(label: Text('Action')),
                            ],
                            source: ChannelDataSource(_filteredChannels,context,_navigateToPage,_showDeleteDialog),
                          ),
                      ),
                ),
              ],
            ),
          );
  }
}

class ChannelDataSource extends DataTableSource {
  final List<Map<String, dynamic>> _channels;
  final BuildContext context;
  final Future<void> Function(BuildContext, String, Map<String, dynamic>) navigateToPage;
  final void Function(String) showDeleteDialog;

  ChannelDataSource(this._channels, this.context, this.navigateToPage, this.showDeleteDialog);

  @override
  DataRow getRow(int index) {
    final channel = _channels[index];
    int sensorCount = 0;
    if (channel['sensor'] != null && channel['sensor'] is List) {
      sensorCount = (channel['sensor'] as List).length;
    }
    return DataRow(cells: [
      DataCell(Text(channel['channel_name'] ?? '')),
      DataCell(Text(channel['description'] ?? '')),
      DataCell(Text(channel['date_created'] ?? '')),
      DataCell(Text(channel['date_modified'] ?? '')),
      DataCell(Text(sensorCount.toString())),
      DataCell(Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          IconButton(
            icon: const Icon(Icons.remove_red_eye, color: Colors.blue),
            tooltip: "View Channel",
            onPressed: () => navigateToPage(context, "View", channel),
          ),
          IconButton(
            icon: const Icon(Icons.edit, color: Colors.orange),
            tooltip: "Edit Channel",
            onPressed: () => navigateToPage(context, "Edit", channel),
          ),
          IconButton(
            icon: const Icon(Icons.delete, color: Colors.red),
            tooltip: "Delete Channel",
            onPressed: () => showDeleteDialog(channel['_id'].toString()),
          ),
        ],
      )),
    ]);
  }

  @override
  int get rowCount => _channels.length;

  @override
  bool get isRowCountApproximate => false;

  @override
  int get selectedRowCount => 0;
}


class PlaceholderPage extends StatelessWidget {
  final String action;
  final String channelName;

  const PlaceholderPage({super.key, required this.action, required this.channelName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("$action Channel")),
      body: Center(
        child: Text(
          "This is the placeholder page for $action on channel: $channelName",
          style: const TextStyle(fontSize: 18),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }
}
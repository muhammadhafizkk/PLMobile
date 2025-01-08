import 'dart:convert';
import 'package:http/http.dart' as http;

class ChannelService {
  static const String apiUrl = "http://10.0.2.2:8000/mychannel/";

  // Function to fetch the channel data
  Future<List<Map<String, dynamic>>> fetchChannels() async {
    try {
      final response = await http.get(Uri.parse(apiUrl));

      if (response.statusCode == 200) {
        List<dynamic> data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data);
      } else {
        throw Exception('Failed to load channels');
      }
    } catch (e) {
      print("Error fetching channels: $e");
      return [];
    }
  }
}

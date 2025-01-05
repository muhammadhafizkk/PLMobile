import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

class DeleteChannelDialog extends StatefulWidget {
  final String channelId;
  final VoidCallback onDelete;

  const DeleteChannelDialog({
    required this.channelId,
    required this.onDelete,
    super.key,
  });

  @override
  _DeleteChannelDialogState createState() => _DeleteChannelDialogState();
}

class _DeleteChannelDialogState extends State<DeleteChannelDialog> {
  bool _isLoading = false;

  // Method to delete the channel
  Future<void> _deleteChannel(String channelId, BuildContext context) async {
    setState(() {
      _isLoading = true;
    });

    const String apiUrl = "http://10.0.2.2:8000/channels/delete/"; // URL for delete API
    try {
      final response = await http.delete(Uri.parse('$apiUrl$channelId'));
      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Channel deleted successfully')),
        );
        widget.onDelete(); // Callback to refresh the list of channels
      } else {
        throw Exception('Failed to delete the channel');
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error deleting channel: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });

      // Ensure the dialog closes only after the process is finished
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Delete Channel'),
      content: _isLoading
          ? const Center(child: CircularProgressIndicator()) // Show loading indicator
          : const Text('Are you sure you want to delete this channel?'),
      actions: [
        TextButton(
          onPressed: _isLoading
              ? null // Disable Cancel button while loading
              : () {
                  Navigator.of(context).pop(); // Close the dialog if Cancel is pressed
                },
          child: const Text('Cancel'),
        ),
        TextButton(
          onPressed: _isLoading
              ? null // Disable Delete button while loading
              : () {
                  _deleteChannel(widget.channelId, context); // Start deletion
                },
          child: const Text('Delete'),
        ),
      ],
    );
  }
}

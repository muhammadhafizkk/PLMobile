// ignore_for_file: use_build_context_synchronously
import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:plflutter/location_dropdown.dart'; // Import the LocationDropdown

class EditChannelPage extends StatefulWidget {
  final Map<String, dynamic> channel;

  const EditChannelPage({super.key, required this.channel});

  @override
  State<EditChannelPage> createState() => _EditChannelPageState();
}

class _EditChannelPageState extends State<EditChannelPage> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  String? _selectedState;
  String? _selectedDistrict;
  String? _privacy;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    // Initialize controllers with the current channel data
    _nameController = TextEditingController(text: widget.channel['channel_name']);
    _descriptionController = TextEditingController(text: widget.channel['description']);

    // Parse location if available
    final location = widget.channel['location']?.split(', ');
    _selectedState = location?.isNotEmpty == true ? location![0] : null;
    _selectedDistrict = location?.length == 2 ? location[1] : null;

    _privacy = widget.channel['privacy'];
  }

  Future<void> _saveChanges() async {
    if (_formKey.currentState!.validate() && !_isSubmitting) {
      setState(() {
        _isSubmitting = true; // Disable button while submitting
      });

      try {
        final response = await http.put(
          Uri.parse("http://10.0.2.2:8000/mychannels/${widget.channel['_id']}/edit"),
          headers: {'Content-Type': 'application/json'},
          body: json.encode({
            'channel_name': _nameController.text,
            'description': _descriptionController.text,
            'location': '${_selectedState ?? ''}, ${_selectedDistrict ?? ''}',
            'privacy': _privacy,
          }),
        );

        if (response.statusCode == 200) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Channel updated successfully!')),
          );
          Navigator.pop(context, true); // Go back to the previous page
        } else if (response.statusCode == 400) {
          // Handle duplicate channel name error
          final Map<String, dynamic> responseData = json.decode(response.body);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(responseData['error'] ?? 'Failed to edit channel')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: ${response.body}')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      } finally {
        setState(() {
          _isSubmitting = false; // Re-enable button after process
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Channel'),
        backgroundColor: Colors.orange,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Channel Name'),
                maxLength: 20,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a channel name';
                  }
                  return null;
                },
              ),
              TextFormField(
                controller: _descriptionController,
                decoration: const InputDecoration(labelText: 'Description'),
                maxLength: 50,
                validator: (value) {
                  if (value == null || value.isEmpty || value.length < 5) {
                    return 'Enter a description at least 5 characters long';
                  }
                  return null;
                },
              ),
              // Location Dropdown
              LocationDropdown(
                onLocationSelected: (state, district) {
                  setState(() {
                    _selectedState = state;
                    _selectedDistrict = district;
                  });
                },
                initialState: _selectedState, // Pass the initial state
                initialDistrict: _selectedDistrict, // Pass the initial district
              ),
              DropdownButtonFormField<String>(
                value: _privacy,
                items: const [
                  DropdownMenuItem(value: 'public', child: Text('public')),
                  DropdownMenuItem(value: 'private', child: Text('private')),
                ],
                onChanged: (value) {
                  setState(() {
                    _privacy = value;
                  });
                },
                decoration: const InputDecoration(labelText: 'Privacy'),
                validator: (value) {
                  if (value == null) {
                    return 'Please select a privacy option';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _isSubmitting ? null : _saveChanges,
                child: _isSubmitting
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Save Changes'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}


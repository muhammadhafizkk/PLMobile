import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:plflutter/location_dropdown.dart';

class CreateChannel extends StatelessWidget {
  const CreateChannel({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Create Channel'),
        backgroundColor: Colors.green[300],
        centerTitle: true,
      ),
      body: const ChannelForm(),
    );
  }
}

class ChannelForm extends StatefulWidget {
  const ChannelForm({super.key});

  @override
  State<ChannelForm> createState() => _ChannelFormState();
}

class _ChannelFormState extends State<ChannelForm> {
  final _formGlobalKey = GlobalKey<FormState>();
  bool _isSubmitting = false;

  // Variables to store form inputs
  String _channelName = '';
  String _description = '';
  String? _selectedState;
  String? _selectedDistrict;
  String? _selectedPrivacy = 'private';

  final List<DropdownMenuItem<String>> _privacyOptions = [
    const DropdownMenuItem(value: 'public', child: Text('public')),
    const DropdownMenuItem(value: 'private', child: Text('private')),
  ];

  // Submit form data to backend
  Future<void> submitForm() async {
    setState(() {
      _isSubmitting = true; // Disable the button
    });

    const String apiUrl = "http://10.0.2.2:8000/mychannels/create/";

    try {
      final response = await http.post(
        Uri.parse(apiUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'channel_name': _channelName,
          'description': _description,
          'location': '${_selectedState ?? ''}, ${_selectedDistrict ?? ''}',
          'privacy': _selectedPrivacy,
        }),
      );

      if (response.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Channel created successfully!')),
        );
        Navigator.pushNamed(context, '/channels'); // Navigate after success
      } else if (response.statusCode == 400) {
      // Handle duplicate channel name error
      final Map<String, dynamic> responseData = json.decode(response.body);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(responseData['error'] ?? 'Failed to create channel')),
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
        _isSubmitting = false; // Re-enable the button
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          const Text(
            'Create a Channel',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          Form(
            key: _formGlobalKey,
            child: Column(
              children: [
                // Channel Name
                TextFormField(
                  maxLength: 20,
                  decoration: const InputDecoration(
                    labelText: 'Channel Name',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Enter a name for the channel';
                    }
                    return null;
                  },
                  onSaved: (value) => _channelName = value!,
                ),

                // Channel Description
                TextFormField(
                  maxLength: 50,
                  decoration: const InputDecoration(
                    labelText: 'Channel Description',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty || value.length < 5) {
                      return 'Enter a description at least 5 characters long';
                    }
                    return null;
                  },
                  onSaved: (value) => _description = value!,
                ),

                // Location Dropdown
                LocationDropdown(
                  onLocationSelected: (state, district) {
                    setState(() {
                      _selectedState = state;
                      _selectedDistrict = district;
                    });
                  },
                ),

                // Privacy
                DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Privacy',
                  ),
                  items: _privacyOptions,
                  value: _selectedPrivacy,
                  onChanged: (value) {
                    setState(() {
                      _selectedPrivacy = value;
                    });
                  },
                  validator: (value) {
                    if (value == null) {
                      return 'Select a privacy option';
                    }
                    return null;
                  },
                ),

                const SizedBox(height: 20),

                // Submit Button
                ElevatedButton(
                  onPressed: _isSubmitting
                      ? null
                      : () {
                          if (_formGlobalKey.currentState!.validate()) {
                            _formGlobalKey.currentState!.save(); // Save field values
                            submitForm();
                          }
                        },
                  child: _isSubmitting
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text('Create'),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

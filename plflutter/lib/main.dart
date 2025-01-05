import 'package:flutter/material.dart';
import 'package:plflutter/home_page.dart';
import 'package:plflutter/viewchannel_page.dart';
import 'package:plflutter/createchannel_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'PlantLink',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const Home(),
      routes: {
        '/channels': (context) => const ViewChannel(),
        '/channels/create': (context) => const CreateChannel(), 
      },  // Display the ChannelTable widget
    );
  }
}
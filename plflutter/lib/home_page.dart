import 'package:flutter/material.dart';

class Home extends StatelessWidget {
  const Home({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('PlantLink'),
        backgroundColor: Colors.green[300],
        centerTitle: true,),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            color: Colors.blue[200],
            child: const RowNumber1(),
          ),
          Expanded(
            child: Image.asset('assets/plantbg.jpg',
            fit: BoxFit.fitWidth,
            alignment: Alignment.bottomCenter,),
          ),
        ],
      ),
    );
  }
}

class RowNumber1 extends StatelessWidget {
  const RowNumber1({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        ElevatedButton(
          onPressed: () {
            Navigator.pushNamed(context, '/channels'); 
          },
          child: const Text('My Channels'),
        ),
      ],
    );
  }
}

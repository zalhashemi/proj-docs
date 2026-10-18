import 'package:flutter/material.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Your trails')),
      body: const Center(child: Text('Plan your first hike')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        label: const Text('New trail'),
      ),
    );
  }
}

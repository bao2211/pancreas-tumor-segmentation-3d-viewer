import 'dart:convert';
import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../widgets/glass_card.dart';

class NiiViewerScreen extends StatefulWidget {
  final List<Map<String, dynamic>> slices;
  final String fileName;

  const NiiViewerScreen({
    super.key,
    required this.slices,
    required this.fileName,
  });

  @override
  State<NiiViewerScreen> createState() => _NiiViewerScreenState();
}

class _NiiViewerScreenState extends State<NiiViewerScreen> {
  int _currentIndex = 0;
  
  @override
  void initState() {
    super.initState();
    // Start at middle slice roughly
    if (widget.slices.isNotEmpty) {
      _currentIndex = widget.slices.length ~/ 2;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.slices.isEmpty) {
       return Scaffold(
          backgroundColor: AppTheme.background,
          appBar: AppBar(title: Text(widget.fileName)),
          body: const Center(child: Text("No slices found", style: TextStyle(color: Colors.white))),
       );
    }
    
    final currentSlice = widget.slices[_currentIndex];
    final imageBytes = base64Decode(currentSlice['image']);

    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text('${widget.fileName} - Slice $_currentIndex/${widget.slices.length - 1}'),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.white),
        titleTextStyle: const TextStyle(color: Colors.white, fontSize: 20),
      ),
      body: Column(
        children: [
          Expanded(
            child: Center(
              child: GlassCard(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Image.memory(
                    imageBytes,
                    fit: BoxFit.contain,
                    width: 500,
                    height: 500,
                    gaplessPlayback: true,
                  ),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: GlassCard(
              child: Column(
                children: [
                  Text(
                    "Scroll to navigate",
                    style: TextStyle(color: AppTheme.textSecondary),
                  ),
                  Slider(
                    value: _currentIndex.toDouble(),
                    min: 0,
                    max: (widget.slices.length - 1).toDouble(),
                    divisions: widget.slices.length - 1 > 0 ? widget.slices.length - 1 : 1,
                    onChanged: (value) {
                      setState(() {
                         _currentIndex = value.toInt();
                      });
                    },
                    activeColor: AppTheme.primaryBlue,
                  ),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                       IconButton(
                         icon: const Icon(Icons.arrow_back_ios, color: Colors.white),
                         onPressed: _currentIndex > 0 
                           ? () => setState(() => _currentIndex--) 
                           : null,
                       ),
                       Text(
                         "Slice $_currentIndex",
                         style: const TextStyle(
                           color: Colors.white, 
                           fontWeight: FontWeight.bold,
                           fontSize: 18,
                         ),
                       ),
                       IconButton(
                         icon: const Icon(Icons.arrow_forward_ios, color: Colors.white),
                         onPressed: _currentIndex < widget.slices.length - 1
                           ? () => setState(() => _currentIndex++) 
                           : null,
                       ),
                    ],
                  )
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

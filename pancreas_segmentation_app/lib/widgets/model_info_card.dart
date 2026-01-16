import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'glass_card.dart';

class ModelInfoCard extends StatelessWidget {
  const ModelInfoCard({super.key});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryPurple.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.memory,
                  color: AppTheme.primaryPurple,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              const Text(
                'AI Model Information',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          
          // Two-Stage Architecture
          _buildInfoSection(
            'Architecture',
            'Two-Stage U-Net',
            Icons.architecture,
            AppTheme.primaryBlue,
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSubInfo('Stage 1: Pancreas Detection (256×256)'),
                _buildSubInfo('Stage 2: Tumor Detection (128×128 ROI)'),
              ],
            ),
          ),
          
          const Divider(height: 24, color: AppTheme.surfaceCardHover),
          
          // Preprocessing
          _buildInfoSection(
            'Preprocessing',
            'HU Windowing [-128, 127]',
            Icons.tune,
            AppTheme.accentTeal,
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSubInfo('Hounsfield Unit normalization to [0, 1]'),
                _buildSubInfo('ROI cropping for tumor detection'),
              ],
            ),
          ),
          
          const Divider(height: 24, color: AppTheme.surfaceCardHover),
          
          // Context-Aware System
          _buildInfoSection(
            'Enhancement',
            'Context-Aware Prediction',
            Icons.spatial_tracking,
            AppTheme.warning,
          ),
          const SizedBox(height: 4),
          Padding(
            padding: const EdgeInsets.only(left: 36),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSubInfo('Temporal smoothing across slices'),
                _buildSubInfo('Morphological operations for continuity'),
                _buildSubInfo('Connected component analysis'),
              ],
            ),
          ),
          
          const Divider(height: 24, color: AppTheme.surfaceCardHover),
          
          // Dataset
          _buildInfoSection(
            'Training Dataset',
            'MSD Task07 Pancreas',
            Icons.dataset,
            AppTheme.success,
          ),
        ],
      ),
    );
  }
  
  Widget _buildInfoSection(String label, String value, IconData icon, Color color) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppTheme.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 13,
                  color: AppTheme.textPrimary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
  
  Widget _buildSubInfo(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            '• ',
            style: TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 11,
            ),
          ),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                fontSize: 11,
                color: AppTheme.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

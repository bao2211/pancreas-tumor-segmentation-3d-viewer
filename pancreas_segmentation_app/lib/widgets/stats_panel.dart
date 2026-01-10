import 'package:flutter/material.dart';
import '../services/ml_service.dart';
import '../theme/app_theme.dart';
import 'glass_card.dart';

class StatsPanel extends StatelessWidget {
  final SegmentationResult result;

  const StatsPanel({super.key, required this.result});

  @override
  Widget build(BuildContext context) {
    final tumorDetected = result.tumorPixelCount > 0;
    
    return GlassCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: tumorDetected 
                      ? AppTheme.tumorRed.withOpacity(0.2)
                      : AppTheme.success.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  tumorDetected ? Icons.warning_rounded : Icons.check_circle,
                  color: tumorDetected ? AppTheme.tumorRed : AppTheme.success,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Analysis Results',
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    Text(
                      tumorDetected 
                          ? 'Potential tumor region detected'
                          : 'No abnormalities detected',
                      style: TextStyle(
                        fontSize: 11,
                        color: tumorDetected 
                            ? AppTheme.tumorRed 
                            : AppTheme.success,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 20),
          
          // Tumor Coverage Bar
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text(
                    'Tumor Coverage',
                    style: TextStyle(
                      fontSize: 12,
                      color: AppTheme.textSecondary,
                    ),
                  ),
                  Text(
                    '${result.tumorPercentage.toStringAsFixed(2)}%',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(
                  value: result.tumorPercentage / 100,
                  backgroundColor: AppTheme.surfaceDark,
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getCoverageColor(result.tumorPercentage),
                  ),
                  minHeight: 8,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          const Divider(height: 1, color: AppTheme.surfaceCardHover),
          const SizedBox(height: 16),
          
          // Stats Grid
          Row(
            children: [
              Expanded(
                child: _buildStatItem(
                  'Affected Pixels',
                  _formatNumber(result.tumorPixelCount),
                  Icons.grid_on,
                ),
              ),
              Container(
                width: 1,
                height: 40,
                color: AppTheme.surfaceCardHover,
              ),
              Expanded(
                child: _buildStatItem(
                  'Resolution',
                  '${result.maskWidth}×${result.maskHeight}',
                  Icons.aspect_ratio,
                ),
              ),
            ],
          ),
          
          const SizedBox(height: 16),
          
          // Severity Indicator
          if (tumorDetected)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.surfaceDark,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.info_outline,
                    size: 16,
                    color: AppTheme.warning,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'This analysis is for reference only. Please consult a medical professional.',
                      style: TextStyle(
                        fontSize: 10,
                        color: AppTheme.textSecondary,
                        height: 1.4,
                      ),
                    ),
                  ),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 18, color: AppTheme.textSecondary),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: const TextStyle(
            fontSize: 10,
            color: AppTheme.textSecondary,
          ),
        ),
      ],
    );
  }

  Color _getCoverageColor(double percentage) {
    if (percentage < 1) return AppTheme.success;
    if (percentage < 5) return AppTheme.warning;
    return AppTheme.tumorRed;
  }

  String _formatNumber(int number) {
    if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }
}

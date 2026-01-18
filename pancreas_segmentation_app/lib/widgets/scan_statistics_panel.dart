import 'package:flutter/material.dart';
import '../models/nii_scan.dart';
import '../theme/app_theme.dart';
import 'glass_card.dart';

class ScanStatisticsPanel extends StatelessWidget {
  final NiiScan scan;
  
  const ScanStatisticsPanel({
    super.key,
    required this.scan,
  });

  @override
  Widget build(BuildContext context) {
    if (!scan.isFullyScanned) {
      return const SizedBox.shrink();
    }
    
    return Column(
      children: [
        // Overall Summary Card
        GlassCard(
          gradient: scan.hasAnyTumor 
              ? LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Colors.orange.shade900.withValues(alpha: 0.3),
                    Colors.red.shade900.withValues(alpha: 0.2),
                  ],
                )
              : null,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(
                    scan.hasAnyTumor 
                        ? Icons.warning_amber_rounded 
                        : Icons.check_circle_outline,
                    color: scan.hasAnyTumor ? Colors.orange : AppTheme.success,
                    size: 28,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          scan.hasAnyTumor 
                              ? '⚠️ Tumor Detected' 
                              : '✓ No Tumor Found',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: scan.hasAnyTumor 
                                ? Colors.orange 
                                : AppTheme.success,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          scan.hasAnyTumor
                              ? 'Suspicious regions identified in ${scan.numWithTumor} slice(s)'
                              : 'All scanned slices appear normal',
                          style: const TextStyle(
                            fontSize: 12,
                            color: AppTheme.textSecondary,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              
              if (scan.hasAnyTumor) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.orange.withValues(alpha: 0.3),
                      width: 1,
                    ),
                  ),
                  child: const Row(
                    children: [
                      Icon(
                        Icons.priority_high,
                        color: Colors.orange,
                        size: 20,
                      ),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'AI-assisted detection: Requires clinical validation',
                          style: TextStyle(
                            fontSize: 11,
                            color: AppTheme.textSecondary,
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Volume Information
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSectionHeader('Volume Information', Icons.view_in_ar),
              const SizedBox(height: 12),
              _buildStatRow('Dimensions', scan.volumeDimensions, Icons.straighten),
              _buildStatRow('Total Slices', '${scan.numSlices}', Icons.layers),
              _buildStatRow('Scanned Slices', '${scan.numScanned}', Icons.check_circle),
            ],
          ),
        ),
        
        const SizedBox(height: 12),
        
        // Pancreas Detection Statistics
        GlassCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildSectionHeader('Pancreas Detection', Icons.biotech, color: AppTheme.accentTeal),
              const SizedBox(height: 12),
              _buildStatRow(
                'Slices with Pancreas',
                '${scan.numWithPancreas} / ${scan.numScanned}',
                Icons.pie_chart,
              ),
              _buildPercentageBar(
                scan.pancreasSlicePercentage,
                AppTheme.accentTeal,
              ),
              const SizedBox(height: 8),
              _buildStatRow(
                'Total Pancreas Pixels',
                _formatNumber(scan.totalPancreasPixels),
                Icons.grid_on,
              ),
            ],
          ),
        ),
        
        if (scan.hasAnyTumor) ...[
          const SizedBox(height: 12),
          
          // Tumor Detection Statistics
          GlassCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildSectionHeader('Tumor Analysis', Icons.coronavirus, color: Colors.orange),
                const SizedBox(height: 12),
                
                // Tumor Burden - Most Important Metric
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.orange.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Tumor Burden',
                            style: TextStyle(
                              fontSize: 13,
                              color: AppTheme.textSecondary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          Text(
                            '${scan.tumorBurden.toStringAsFixed(2)}%',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.orange,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Percentage of tumor relative to pancreas tissue',
                        style: TextStyle(
                          fontSize: 10,
                          color: AppTheme.textSecondary,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 12),
                
                _buildStatRow(
                  'Affected Slices',
                  '${scan.numWithTumor} / ${scan.numWithPancreas}',
                  Icons.layers_outlined,
                ),
                _buildPercentageBar(
                  scan.tumorSlicePercentage,
                  Colors.orange,
                ),
                
                const SizedBox(height: 8),
                
                _buildStatRow(
                  'Total Tumor Pixels',
                  _formatNumber(scan.totalTumorPixels),
                  Icons.grid_on,
                ),
                
                _buildStatRow(
                  'Avg Tumor per Slice',
                  _formatNumber(scan.avgTumorPixelsPerSlice.round()),
                  Icons.analytics,
                ),
                
                _buildStatRow(
                  'Max Tumor in Slice',
                  '${_formatNumber(scan.maxTumorPixelsInSlice)} (Slice ${scan.maxTumorSliceIndex})',
                  Icons.arrow_upward,
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
  
  Widget _buildSectionHeader(String title, IconData icon, {Color? color}) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: (color ?? AppTheme.primaryBlue).withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(6),
          ),
          child: Icon(
            icon,
            color: color ?? AppTheme.primaryBlue,
            size: 16,
          ),
        ),
        const SizedBox(width: 10),
        Text(
          title,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            color: AppTheme.textPrimary,
          ),
        ),
      ],
    );
  }
  
  Widget _buildStatRow(String label, String value, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 14, color: AppTheme.textSecondary),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 12,
                color: AppTheme.textSecondary,
              ),
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppTheme.textPrimary,
            ),
          ),
        ],
      ),
    );
  }
  
  Widget _buildPercentageBar(double percentage, Color color) {
    return Padding(
      padding: const EdgeInsets.only(left: 22, top: 4),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: percentage / 100,
              minHeight: 6,
              backgroundColor: AppTheme.surfaceDark,
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
          const SizedBox(height: 2),
          Text(
            '${percentage.toStringAsFixed(1)}%',
            style: TextStyle(
              fontSize: 10,
              color: color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
  
  String _formatNumber(int number) {
    if (number >= 1000000) {
      return '${(number / 1000000).toStringAsFixed(2)}M';
    } else if (number >= 1000) {
      return '${(number / 1000).toStringAsFixed(1)}K';
    }
    return number.toString();
  }
}

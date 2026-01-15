import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class StatusIndicator extends StatelessWidget {
  final bool isConnected;
  final String label;
  final VoidCallback? onRetry;

  const StatusIndicator({
    super.key,
    required this.isConnected,
    required this.label,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onRetry,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: isConnected 
              ? AppTheme.success.withOpacity(0.15)
              : AppTheme.warning.withOpacity(0.15),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isConnected 
                ? AppTheme.success.withOpacity(0.3)
                : AppTheme.warning.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isConnected ? AppTheme.success : AppTheme.warning,
                boxShadow: [
                  BoxShadow(
                    color: (isConnected ? AppTheme.success : AppTheme.warning)
                        .withOpacity(0.5),
                    blurRadius: 6,
                    spreadRadius: 1,
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: isConnected ? AppTheme.success : AppTheme.warning,
              ),
            ),
            if (!isConnected && onRetry != null) ...[
              const SizedBox(width: 4),
              const Icon(
                Icons.refresh,
                size: 14,
                color: AppTheme.warning,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';

import '../design/tokens/colors.dart';
import '../design/tokens/radius.dart';
import '../design/tokens/shadows.dart';
import '../design/tokens/spacing.dart';
import '../design/tokens/typography.dart';

class CardPanel extends StatelessWidget {
  const CardPanel({
    super.key,
    required this.title,
    this.icon,
    this.trailing,
    this.highlighted = false,
    this.compact = false,
    this.fillHeight = false,
    required this.child,
  });

  final String title;
  final IconData? icon;
  final Widget? trailing;
  final bool highlighted;
  final bool compact;
  final bool fillHeight;
  final Widget child;

  @override
  Widget build(BuildContext context) {
    final padding = EdgeInsets.all(compact ? AppSpacing.s4 : AppSpacing.s5);

    final decoration = BoxDecoration(
      color: AppColors.bgElevated1,
      gradient: highlighted ? AppColors.todayCardGradient : null,
      borderRadius: BorderRadius.circular(AppRadius.xl),
      border: Border.all(
        color: highlighted ? AppColors.borderEmphasis : AppColors.borderSubtle,
      ),
      boxShadow: highlighted ? AppShadows.glowCyan : AppShadows.card,
    );

    final body = Container(
      padding: padding,
      decoration: decoration,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: fillHeight ? MainAxisSize.max : MainAxisSize.min,
        children: [
          Row(
            children: [
              if (icon != null) ...[
                Icon(
                  icon,
                  size: 18,
                  color: highlighted
                      ? AppColors.accentPrimary
                      : AppColors.textSecondary,
                ),
                const SizedBox(width: AppSpacing.s2),
              ],
              Expanded(
                child: Text(
                  title,
                  style: AppTypography.h3.copyWith(
                    color: highlighted
                        ? AppColors.accentPrimary
                        : AppColors.textPrimary,
                  ),
                ),
              ),
              if (trailing != null) trailing!,
            ],
          ),
          const SizedBox(height: AppSpacing.s4),
          if (fillHeight) Expanded(child: child) else child,
        ],
      ),
    );

    return fillHeight ? SizedBox.expand(child: body) : body;
  }
}

class PlaceholderPanel extends StatelessWidget {
  const PlaceholderPanel({
    super.key,
    required this.title,
    required this.icon,
    required this.note,
    this.fillHeight = false,
  });

  final String title;
  final IconData icon;
  final String note;
  final bool fillHeight;

  @override
  Widget build(BuildContext context) {
    return CardPanel(
      title: title,
      icon: icon,
      fillHeight: fillHeight,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: AppSpacing.s5),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                LucideIcons.sparkles,
                size: 18,
                color: AppColors.textTertiary,
              ),
              const SizedBox(height: AppSpacing.s2),
              Text(
                note,
                textAlign: TextAlign.center,
                style: AppTypography.caption.copyWith(
                  color: AppColors.textTertiary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

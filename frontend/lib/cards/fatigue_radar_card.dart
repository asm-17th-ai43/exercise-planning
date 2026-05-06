import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:lucide_icons/lucide_icons.dart';

import '../design/tokens/colors.dart';
import '../design/tokens/spacing.dart';
import '../design/tokens/typography.dart';
import '../models/muscle_fatigue_state.dart';
import 'card_panel.dart';

class FatigueRadarCard extends StatelessWidget {
  const FatigueRadarCard({super.key, required this.state});

  final MuscleFatigueState state;

  @override
  Widget build(BuildContext context) {
    final entries = state.fatigue.entries.toList(growable: false);

    return CardPanel(
      title: '부위별 피로도',
      icon: LucideIcons.sparkles,
      trailing: Text(
        '0–5 스케일 · 데모',
        style: AppTypography.caption.copyWith(color: AppColors.textTertiary),
      ),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s3),
        child: SizedBox(
          height: 280,
          child: RadarChart(
            RadarChartData(
              radarShape: RadarShape.polygon,
              tickCount: 4,
              tickBorderData: const BorderSide(
                color: AppColors.borderSubtle,
                width: 1,
              ),
              gridBorderData: const BorderSide(
                color: AppColors.borderSubtle,
                width: 1,
              ),
              radarBorderData:
                  const BorderSide(color: AppColors.borderSubtle, width: 1),
              borderData: FlBorderData(show: false),
              titleTextStyle: AppTypography.caption.copyWith(
                color: AppColors.textSecondary,
              ),
              getTitle: (index, angle) =>
                  RadarChartTitle(text: entries[index].key),
              ticksTextStyle: const TextStyle(
                color: Colors.transparent,
                fontSize: 10,
              ),
              radarBackgroundColor: Colors.transparent,
              dataSets: [
                RadarDataSet(
                  fillColor: AppColors.accentPrimary.withValues(alpha: 0.2),
                  borderColor: AppColors.accentPrimary,
                  borderWidth: 2,
                  entryRadius: 4,
                  dataEntries: [
                    for (final e in entries)
                      RadarEntry(value: e.value.toDouble()),
                  ],
                ),
              ],
              radarTouchData: RadarTouchData(enabled: false),
            ),
          ),
        ),
      ),
    );
  }
}

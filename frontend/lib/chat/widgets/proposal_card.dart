import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:lucide_icons/lucide_icons.dart';

import '../../design/tokens/colors.dart';
import '../../design/tokens/radius.dart';
import '../../design/tokens/spacing.dart';
import '../../design/tokens/typography.dart';
import '../chat_message.dart';

/// Renders a [ScheduleProposal] as a stack of slot cards inside the chat
/// transcript. The "캘린더에 등록" button (F7) is added in 5/8.
class ProposalCard extends StatelessWidget {
  const ProposalCard({super.key, required this.proposal});

  final ScheduleProposal proposal;

  @override
  Widget build(BuildContext context) {
    if (proposal.slots.isEmpty) return const SizedBox.shrink();

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppSpacing.s4),
      decoration: BoxDecoration(
        gradient: AppColors.recommendGradient,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Icon(LucideIcons.sparkles,
                  size: 14, color: AppColors.accentPrimary),
              const SizedBox(width: AppSpacing.s2),
              Text(
                '추천 운동 슬롯',
                style: AppTypography.caption.copyWith(
                  color: AppColors.accentPrimary,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.s3),
          for (var i = 0; i < proposal.slots.length; i++) ...[
            if (i != 0) const SizedBox(height: AppSpacing.s2),
            _SlotRow(slot: proposal.slots[i]),
          ],
        ],
      ),
    );
  }
}

class _SlotRow extends StatelessWidget {
  const _SlotRow({required this.slot});

  final WorkoutSlot slot;

  @override
  Widget build(BuildContext context) {
    final dayLabel = DateFormat('M/d (E)', 'ko_KR').format(slot.start);
    final timeLabel =
        '${DateFormat('HH:mm').format(slot.start)}–${DateFormat('HH:mm').format(slot.end)}';

    return Container(
      padding: const EdgeInsets.all(AppSpacing.s3),
      decoration: BoxDecoration(
        color: AppColors.bgElevated1,
        borderRadius: BorderRadius.circular(AppRadius.md),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Expanded(
                child: Text(
                  '$dayLabel · $timeLabel',
                  style: AppTypography.caption.copyWith(
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
              _IntensityChip(intensity: slot.intensity),
            ],
          ),
          const SizedBox(height: AppSpacing.s1),
          Text(
            '${slot.type} · ${slot.targetMuscles.join(', ')}',
            style: AppTypography.body.copyWith(fontWeight: FontWeight.w600),
          ),
          if (slot.rationale.isNotEmpty) ...[
            const SizedBox(height: 2),
            Text(
              slot.rationale,
              style: AppTypography.caption,
            ),
          ],
        ],
      ),
    );
  }
}

class _IntensityChip extends StatelessWidget {
  const _IntensityChip({required this.intensity});

  final int intensity;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppSpacing.s2,
        vertical: 2,
      ),
      decoration: BoxDecoration(
        color: AppColors.bgElevated2,
        borderRadius: BorderRadius.circular(AppRadius.full),
      ),
      child: Text(
        '강도 $intensity/5',
        style: AppTypography.overline.copyWith(
          color: AppColors.textSecondary,
        ),
      ),
    );
  }
}

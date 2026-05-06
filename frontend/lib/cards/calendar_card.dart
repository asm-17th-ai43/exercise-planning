import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:lucide_icons/lucide_icons.dart';

import '../api/calendar_api.dart';
import '../design/tokens/colors.dart';
import '../design/tokens/radius.dart';
import '../design/tokens/spacing.dart';
import '../design/tokens/typography.dart';
import '../models/calendar_event.dart';
import 'card_panel.dart';

class CalendarCard extends StatefulWidget {
  const CalendarCard({
    super.key,
    required this.api,
    required this.weekStart,
  });

  final CalendarApi api;
  final DateTime weekStart;

  @override
  State<CalendarCard> createState() => _CalendarCardState();
}

class _CalendarCardState extends State<CalendarCard> {
  late Future<List<CalendarEvent>> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
  }

  Future<List<CalendarEvent>> _load() {
    final end = widget.weekStart.add(const Duration(days: 7));
    return widget.api.getCalendar(widget.weekStart, end);
  }

  @override
  Widget build(BuildContext context) {
    final weekLabel = _weekRangeLabel(widget.weekStart);

    return CardPanel(
      title: '이번 주 일정',
      icon: LucideIcons.calendar,
      trailing: Text(
        weekLabel,
        style: AppTypography.caption.copyWith(color: AppColors.textTertiary),
      ),
      child: FutureBuilder<List<CalendarEvent>>(
        future: _future,
        builder: (context, snapshot) {
          return switch (snapshot.connectionState) {
            ConnectionState.waiting => const _LoadingSkeleton(),
            _ when snapshot.hasError => _ErrorLine(
                message: '일정을 불러오지 못했습니다',
                detail: snapshot.error.toString(),
              ),
            _ => _EventList(events: snapshot.data ?? const []),
          };
        },
      ),
    );
  }
}

String _weekRangeLabel(DateTime weekStart) {
  final end = weekStart.add(const Duration(days: 6));
  final f = DateFormat('M/d');
  return '${f.format(weekStart)} – ${f.format(end)}';
}

class _EventList extends StatelessWidget {
  const _EventList({required this.events});

  final List<CalendarEvent> events;

  @override
  Widget build(BuildContext context) {
    if (events.isEmpty) {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: AppSpacing.s4),
        child: Row(
          children: [
            Icon(
              LucideIcons.calendarOff,
              size: 16,
              color: AppColors.textTertiary,
            ),
            const SizedBox(width: AppSpacing.s2),
            Text(
              '이번 주 등록된 일정이 없습니다',
              style: AppTypography.caption.copyWith(
                color: AppColors.textTertiary,
              ),
            ),
          ],
        ),
      );
    }

    final today = DateTime.now();
    final dayLabel = DateFormat('E', 'ko_KR');
    final timeLabel = DateFormat('HH:mm');

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        for (var i = 0; i < events.length; i++) ...[
          if (i != 0) const Divider(height: 1, color: AppColors.divider),
          _EventRow(
            event: events[i],
            isToday: _isSameDate(events[i].startAt, today),
            dayLabel: dayLabel.format(events[i].startAt),
            timeLabel: timeLabel.format(events[i].startAt),
          ),
        ],
      ],
    );
  }

  static bool _isSameDate(DateTime a, DateTime b) =>
      a.year == b.year && a.month == b.month && a.day == b.day;
}

class _EventRow extends StatelessWidget {
  const _EventRow({
    required this.event,
    required this.isToday,
    required this.dayLabel,
    required this.timeLabel,
  });

  final CalendarEvent event;
  final bool isToday;
  final String dayLabel;
  final String timeLabel;

  @override
  Widget build(BuildContext context) {
    final accentColor =
        event.isBusy ? AppColors.statusDanger : AppColors.statusSuccess;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: AppSpacing.s3),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Container(
            width: 44,
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.s1),
            decoration: BoxDecoration(
              color: isToday
                  ? AppColors.accentPrimary.withValues(alpha: 0.12)
                  : AppColors.bgElevated2,
              borderRadius: BorderRadius.circular(AppRadius.md),
              border: Border.all(
                color: isToday
                    ? AppColors.accentPrimary.withValues(alpha: 0.4)
                    : Colors.transparent,
              ),
            ),
            child: Column(
              children: [
                Text(
                  dayLabel,
                  style: AppTypography.overline.copyWith(
                    color: isToday
                        ? AppColors.accentPrimary
                        : AppColors.textSecondary,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  timeLabel,
                  style: AppTypography.dataMd.copyWith(
                    fontSize: 13,
                    color: isToday
                        ? AppColors.accentPrimary
                        : AppColors.textPrimary,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: AppSpacing.s4),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  event.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: AppTypography.body.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 2),
                Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: accentColor,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: AppSpacing.s2),
                    Text(
                      event.isBusy ? '바쁨' : '운동 가능',
                      style: AppTypography.caption.copyWith(color: accentColor),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _LoadingSkeleton extends StatelessWidget {
  const _LoadingSkeleton();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        for (var i = 0; i < 3; i++)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: AppSpacing.s3),
            child: Row(
              children: [
                Container(
                  width: 44,
                  height: 36,
                  decoration: BoxDecoration(
                    color: AppColors.bgElevated2,
                    borderRadius: BorderRadius.circular(AppRadius.md),
                  ),
                ),
                const SizedBox(width: AppSpacing.s4),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        height: 12,
                        width: double.infinity,
                        color: AppColors.bgElevated2,
                      ),
                      const SizedBox(height: 6),
                      Container(
                        height: 10,
                        width: 80,
                        color: AppColors.bgElevated2,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}

class _ErrorLine extends StatelessWidget {
  const _ErrorLine({required this.message, required this.detail});

  final String message;
  final String detail;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppSpacing.s3),
      decoration: BoxDecoration(
        color: AppColors.statusDangerBg,
        borderRadius: BorderRadius.circular(AppRadius.md),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                LucideIcons.alertCircle,
                size: 16,
                color: AppColors.statusDanger,
              ),
              const SizedBox(width: AppSpacing.s2),
              Text(
                message,
                style: AppTypography.body.copyWith(
                  color: AppColors.statusDanger,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.s2),
          Text(
            detail,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style:
                AppTypography.caption.copyWith(color: AppColors.textTertiary),
          ),
        ],
      ),
    );
  }
}

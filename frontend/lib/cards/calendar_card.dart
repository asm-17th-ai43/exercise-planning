import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:lucide_icons/lucide_icons.dart';

import '../api/calendar_api.dart';
import '../design/tokens/colors.dart';
import '../design/tokens/radius.dart';
import '../design/tokens/spacing.dart';
import '../design/tokens/typography.dart';
import '../models/calendar_event.dart';
import 'calendar_reload_notifier.dart';
import 'card_panel.dart';
import 'card_states.dart';

class CalendarCard extends StatefulWidget {
  const CalendarCard({
    super.key,
    required this.api,
    required this.weekStart,
    this.reloadNotifier,
  });

  final CalendarApi api;
  final DateTime weekStart;
  // Optional pub/sub: bumped by Slice B after inserting events from a
  // proposal so this card refetches without a full page reload.
  final CalendarReloadNotifier? reloadNotifier;

  @override
  State<CalendarCard> createState() => _CalendarCardState();
}

class _CalendarCardState extends State<CalendarCard> {
  late Future<List<CalendarEvent>> _future;

  @override
  void initState() {
    super.initState();
    _future = _load();
    widget.reloadNotifier?.addListener(_onExternalReload);
  }

  @override
  void didUpdateWidget(covariant CalendarCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.reloadNotifier != widget.reloadNotifier) {
      oldWidget.reloadNotifier?.removeListener(_onExternalReload);
      widget.reloadNotifier?.addListener(_onExternalReload);
    }
    if (oldWidget.weekStart != widget.weekStart || oldWidget.api != widget.api) {
      _future = _load();
    }
  }

  @override
  void dispose() {
    widget.reloadNotifier?.removeListener(_onExternalReload);
    super.dispose();
  }

  Future<List<CalendarEvent>> _load() {
    final end = widget.weekStart.add(const Duration(days: 7));
    return widget.api.getCalendar(widget.weekStart, end);
  }

  void _onExternalReload() {
    if (!mounted) return;
    setState(() => _future = _load());
  }

  void _retry() => setState(() => _future = _load());

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
            ConnectionState.waiting => const CardLoadingRows(iconSize: 44),
            _ when snapshot.hasError => CardErrorState(
                message: '일정을 불러오지 못했습니다',
                detail: snapshot.error.toString(),
                onRetry: _retry,
              ),
            _ when (snapshot.data ?? const []).isEmpty => const CardEmptyState(
                icon: LucideIcons.calendarOff,
                message: '이번 주 등록된 일정이 없습니다',
                hint: 'calendar_events 시드를 INSERT 하면 표시됩니다',
              ),
            _ => _EventList(events: snapshot.data!),
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

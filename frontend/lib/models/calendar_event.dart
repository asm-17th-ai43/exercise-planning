import 'package:flutter/foundation.dart';

@immutable
class CalendarEvent {
  const CalendarEvent({
    required this.start,
    required this.end,
    required this.title,
    this.isBusy = true,
  });

  final DateTime start;
  final DateTime end;
  final String title;
  final bool isBusy;

  factory CalendarEvent.fromJson(Map<String, dynamic> row) {
    return CalendarEvent(
      start: DateTime.parse(row['start_at'] as String),
      end: DateTime.parse(row['end_at'] as String),
      title: row['title'] as String,
      isBusy: row['is_busy'] as bool? ?? true,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CalendarEvent &&
          runtimeType == other.runtimeType &&
          start == other.start &&
          end == other.end &&
          title == other.title &&
          isBusy == other.isBusy;

  @override
  int get hashCode => Object.hash(start, end, title, isBusy);
}

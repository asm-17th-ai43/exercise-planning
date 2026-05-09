import 'package:flutter/foundation.dart';

@immutable
class CalendarEvent {
  const CalendarEvent({
    this.id,
    required this.startAt,
    required this.endAt,
    required this.title,
    this.isBusy = true,
  });

  final int? id;
  final DateTime startAt;
  final DateTime endAt;
  final String title;
  final bool isBusy;

  factory CalendarEvent.fromJson(Map<String, dynamic> row) {
    return CalendarEvent(
      id: (row['id'] as num?)?.toInt(),
      startAt: DateTime.parse(row['start_at'] as String),
      endAt: DateTime.parse(row['end_at'] as String),
      title: row['title'] as String,
      isBusy: row['is_busy'] as bool? ?? true,
    );
  }

  /// Insert payload — drops `id` so Postgres assigns it.
  Map<String, dynamic> toInsertJson() => {
        'start_at': startAt.toIso8601String(),
        'end_at': endAt.toIso8601String(),
        'title': title,
        'is_busy': isBusy,
      };

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is CalendarEvent &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          startAt == other.startAt &&
          endAt == other.endAt &&
          title == other.title &&
          isBusy == other.isBusy;

  @override
  int get hashCode => Object.hash(id, startAt, endAt, title, isBusy);
}

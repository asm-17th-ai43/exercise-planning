import 'package:supabase_flutter/supabase_flutter.dart';

import '../models/calendar_event.dart';

class CalendarApi {
  const CalendarApi(this._client);

  final SupabaseClient _client;

  Future<List<CalendarEvent>> getCalendar(DateTime start, DateTime end) async {
    final rows = await _client
        .from('calendar_events')
        .select()
        .gte('start_at', start.toIso8601String())
        .lte('end_at', end.toIso8601String())
        .order('start_at');

    return rows
        .cast<Map<String, dynamic>>()
        .map(CalendarEvent.fromJson)
        .toList(growable: false);
  }

  /// Insert a single event and return the row Postgres echoed back (with the
  /// assigned `id`). Used by Slice B's "캘린더에 등록" action on agent
  /// proposals.
  Future<CalendarEvent> createEvent(CalendarEvent event) async {
    final row = await _client
        .from('calendar_events')
        .insert(event.toInsertJson())
        .select()
        .single();
    return CalendarEvent.fromJson(row);
  }
}

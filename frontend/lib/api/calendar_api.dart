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
}

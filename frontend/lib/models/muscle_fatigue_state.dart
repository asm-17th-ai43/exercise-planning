import 'package:flutter/foundation.dart';

@immutable
class MuscleFatigueState {
  const MuscleFatigueState({required this.date, required this.fatigue});

  final DateTime date;
  final Map<String, int> fatigue;

  // 5/6 데모용 더미. schemas/models.py 의 fatigue 는 0~5 스케일.
  // 5/8 통합 시 C agent SSE proposal 청크 출력으로 대체.
  factory MuscleFatigueState.demo() => MuscleFatigueState(
        date: DateTime.now(),
        fatigue: const {
          '가슴': 3,
          '등': 2,
          '어깨': 4,
          '팔': 2,
          '코어': 3,
          '하체': 1,
        },
      );

  factory MuscleFatigueState.fromJson(Map<String, dynamic> row) {
    final raw = (row['fatigue'] as Map).cast<String, dynamic>();
    return MuscleFatigueState(
      date: DateTime.parse(row['date'] as String),
      fatigue: raw.map((k, v) => MapEntry(k, (v as num).toInt())),
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MuscleFatigueState &&
          runtimeType == other.runtimeType &&
          date == other.date &&
          mapEquals(fatigue, other.fatigue);

  @override
  int get hashCode =>
      Object.hash(date, Object.hashAllUnordered(fatigue.entries));
}

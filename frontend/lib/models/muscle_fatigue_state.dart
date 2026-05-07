import 'package:flutter/foundation.dart';

@immutable
class MuscleFatigueState {
  const MuscleFatigueState({required this.date, required this.fatigue});

  final DateTime date;
  final Map<String, int> fatigue;

  // 데모용 더미. 키 순서·이름은 agent/nodes.py:15 의 `_MUSCLES` 와 일치.
  // 5/8 통합 시 C agent SSE proposal 청크 출력으로 대체.
  factory MuscleFatigueState.demo() => MuscleFatigueState(
        date: DateTime.now(),
        fatigue: const {
          '가슴': 3,
          '등': 2,
          '하체': 1,
          '어깨': 4,
          '코어': 3,
          '이두': 2,
          '삼두': 2,
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

# data/ — 가상 데이터 (JSON)

> **담당**: #1 `calendar.json` · #2 `health.json` · #3 `workouts.json`

실제 Google Calendar / Apple Health 연동은 **MVP 범위 외**. 모든 데이터는 여기 JSON에서만 읽는다.

## 페르소나

> 20대 후반 백엔드 개발자. 잦은 야근으로 평일 일정이 불규칙. 스마트워치로 수면 측정. 헬스/러닝/홈트를 번갈아 하지만 매주 계획이 흔들림.

새 데이터를 추가할 때 **이 페르소나에 일관**되게 작성.

## 스키마 (schemas/models.py와 1:1 매칭)

### `calendar.json` (#1)
```json
{"start": "2026-05-04T09:00:00", "end": "...", "title": "스탠드업", "is_busy": true}
```
- `start/end`는 ISO 8601 (시간대 없음, 로컬 가정)
- `is_busy: false`는 운동 가능한 빈 시간 (점심·퇴근 후 등)

### `health.json` (#2)
```json
{"date": "2026-05-03", "sleep_hours": 7.8, "activity_minutes": 45, "resting_hr": 59}
```
- `sleep_hours`는 float, `activity_minutes`는 int (분)
- `resting_hr`은 옵셔널

### `workouts.json` (#3)
```json
{"date": "2026-05-02", "type": "헬스", "duration_min": 55, "muscles": ["어깨", "삼두"], "intensity": 3}
```
- `muscles`는 한국어 부위명 (`visuals/CLAUDE.md`의 매핑과 일치)
- `intensity`는 1~5

## 엣지 케이스 데이터 (5/7~5/9 추가)

KPI 시나리오 통과를 위해 다음 케이스를 데이터로 만들어둘 것:
- **빈 시간 0**: 1주 내내 일정이 꽉 찬 캘린더 → 10분 대체 루틴 제안 검증
- **수면 부족**: 평균 5시간 이하 → 강도 하향 검증
- **연속 부위**: 같은 부위를 3일 연속 운동 기록 → 피로도 누적 → 회피 검증

별도 파일(`data/edge_cases/*.json`)로 두고 테스트에서만 로드하는 방식 권장.

## 작업 시 주의

- 새 필드 추가 전엔 `schemas/models.py` 모델부터 수정
- 한국어 키워드(`title`, 운동명, 부위명)는 한글 유니코드 그대로 (escape 금지)
- JSON 검증: `python -c "import json; json.load(open('data/<file>.json'))"` 통과해야 PR

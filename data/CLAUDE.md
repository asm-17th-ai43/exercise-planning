# data/ — 가상 데이터 (JSON)

> **담당**: D(박영준) — `calendar.json`, `workouts.json`. E(신승민) — `health.json`, `scenarios/` 5개 적재 주도.

실제 Google Calendar / Apple Health 연동은 **MVP 범위 외**. 모든 데이터는 여기 JSON에서만 읽고 쓴다. (DB 도입은 데모 이후 검토 — schemas/models.py가 사실상 DB 스키마.)

## 디렉토리

```
data/
├── calendar.json      # 데모 페르소나 기본 일정
├── health.json        # 데모 페르소나 기본 컨디션
├── workouts.json      # 데모 페르소나 기본 운동 기록
└── scenarios/         # D/E가 정의하는 데모/테스트 시나리오 3~5개
    └── <scenario>.json
```

## 페르소나 (기본 데이터)

> 20대 후반 백엔드 개발자. 잦은 야근으로 평일 일정이 불규칙. 스마트워치로 수면 측정. 헬스/러닝/홈트를 번갈아 하지만 매주 계획이 흔들림.

새 데이터를 추가할 때 **이 페르소나에 일관**되게 작성.

## 스키마 (schemas/models.py와 1:1 매칭)

### `calendar.json`
```json
{"start": "2026-05-04T09:00:00", "end": "...", "title": "스탠드업", "is_busy": true}
```
- `start/end`는 ISO 8601 (시간대 없음, 로컬 가정)
- `is_busy: false`는 운동 가능한 빈 시간 (점심·퇴근 후 등)

### `health.json`
```json
{"date": "2026-05-03", "sleep_hours": 7.8, "activity_minutes": 45, "resting_hr": 59}
```
- `sleep_hours`는 float, `activity_minutes`는 int (분)
- `resting_hr`은 옵셔널

### `workouts.json`
```json
{"date": "2026-05-02", "type": "헬스", "duration_min": 55, "muscles": ["어깨", "삼두"], "intensity": 3}
```
- `muscles`는 한국어 부위명 (FE 레이더 차트 라벨과 일치)
- `intensity`는 1~5

## scenarios/ — 데모·테스트 시나리오 (D/E)

KPI 5개 + 엣지 케이스를 시나리오 단위로 묶어 보관. 데모 시연용 + 테스트용.

각 시나리오 파일은 (예시 구조):
```json
{
  "name": "꽉 찬 일주일 → 10분 대체 루틴",
  "calendar": [...],
  "health": [...],
  "workouts": [...],
  "expected": {
    "should_propose_short_routine": true,
    "max_slot_minutes": 10
  }
}
```

권장 시나리오:
- **빈 시간 0**: 1주 내내 일정이 꽉 찬 캘린더 → 10분 대체 루틴 제안
- **수면 부족**: 평균 5시간 이하 → 강도 하향
- **연속 부위**: 같은 부위 3일 연속 → 피로도 누적 → 회피
- **멀티턴 재조정**: "화요일은 빼줘" → 해당 일자만 변경
- (자유 1개)

## 작업 시 주의

- 새 필드 추가 전엔 `schemas/models.py` 모델부터 수정
- 한국어 키워드(`title`, 운동명, 부위명)는 한글 유니코드 그대로 (escape 금지)
- JSON 검증: `python -c "import json; json.load(open('data/<file>.json'))"` 통과해야 PR

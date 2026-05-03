# D — 박영준 (CRUD Tool + 시나리오 + 프롬프트 튜닝)

## 한 줄 책임

CRUD Tool 작성 + 데모 시나리오 정의 + 테스트 데이터 + 프롬프트 튜닝 (E와 도메인 분담).

> E와 **도메인 분담은 5/4 데일리 싱크에서** 확정. 권장: D=calendar/workouts, E=health/scenarios.

## 주 디렉토리·파일 (권장 분담 기준)

- `tools/data_tools.py` — `get_/create_/update_/delete_calendar_event`, `_workout` (도메인 분담분)
- `data/calendar.json`, `data/workouts.json` — 데모 페르소나 데이터
- `data/scenarios/*.json` — KPI 시나리오 (E와 공동 적재)
- `agent/prompts.py` 튜닝 — C와 협업
- `backend/api/data.py` — 자기 도메인 라우터(현재 501 stub)에 위임 채우기

## 합의 책임 (5/4 락)

- **C와**: Tool 시그니처 (LangGraph `@tool`로 래핑할 형태). schemas/models.py와 1:1
- **E와**: calendar/health/workouts 도메인 분담 결정
- **A와**: `/data/*` REST 응답 형태 (= Tool 반환값 그대로)

## 일자별 to-do (권장 분담 기준)

| 날짜 | 할 일 | 합격 기준 |
|---|---|---|
| **5/4 (월)** | `data/calendar.json` 더미 5건 / `tools.get_calendar` 1차 구현 (JSON 파싱) | `pytest`에서 1주 범위 호출 시 비어있지 않은 리스트 |
| **5/5 (화)** | `get_calendar` JSON 실파싱 완성 / CRUD 중 첫 write 함수 (`create_calendar_event`) | `POST /data/calendar`로 새 이벤트 추가됨 |
| **5/6 (수)** | `update_/delete_calendar_event` 일부 구현 / 1주치 더미 데이터 보강 (충돌·빈시간 케이스) | 4종 CRUD 모두 200/204 응답 |
| **5/7 (목)** | `data/scenarios/`에 KPI 1·3 시나리오(빈시간 0, 일정 꽉 참) 적재 | `data/scenarios/full_week.json` 등 파일 존재 |
| **5/8 (금)** ★ | write Tool 안정화 (atomic 파일 갱신: 임시 파일 → rename) / B의 F7 호출 검증 | 등록 버튼 클릭 시 `calendar.json` 무손실 갱신 |
| **5/9 (토)** | 시나리오 입력 vs 기대 응답 매칭 정밀화 / 프롬프트 튜닝 (C와) | `pytest -m kpi` 1·3·5번 통과 |
| **5/10 (일)** | 데모용 calendar/workouts 데이터 최종 점검 | 데모 시연 무사고 |

## KPI 시나리오 — 본인 영향

- **1번** 일정 충돌 — calendar 데이터 품질이 핵심
- **3번** 빈 시간 0 주 — `data/scenarios/full_week.json` 적재
- **연속 부위** workouts 데이터 (피로도 누적 검증용)

## 자주 볼 문서·CLAUDE.md

- `tools/CLAUDE.md` ← 본인 슬라이스 (CRUD 시그니처, atomic write)
- `data/CLAUDE.md` ← scenarios/ 구조 + 페르소나
- `schemas/CLAUDE.md` ← Pydantic 모델 (`CalendarEvent`, `WorkoutRecord`)
- `backend/CLAUDE.md` ← `/data/*` 라우터 위임 패턴
- `agent/CLAUDE.md` ← C가 어떻게 Tool을 호출하는지 (`@tool` 래퍼)

## 흔한 함정

- `tools/data_tools.py`는 E와 같이 만짐 → **함수 단위 PR**로 쪼갬 (PR 제목에 `[tools] create_calendar_event 구현`)
- write는 read-modify-write — 동시성 걱정 없지만 atomic하게 (임시 파일 → `os.replace`)
- 한국어 키워드(부위명, title) escape 금지 — JSON 한글 그대로
- 새 필드 추가는 `schemas/models.py` 먼저 수정 후 JSON 갱신
- "유저가 FE에서 보는 모든 데이터는 agent도 본다" — A 화면에 새 필드 추가하려면 D/E도 Tool 추가 필수

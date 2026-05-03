# E — 신승민 (CRUD Tool + 시나리오 + 프롬프트 튜닝)

## 한 줄 책임

CRUD Tool 작성 + 데모 시나리오 정의 + 테스트 데이터 + 프롬프트 튜닝 (D와 도메인 분담).

> D와 **도메인 분담은 5/4 데일리 싱크에서** 확정. 권장: D=calendar/workouts, E=health/scenarios.

## 주 디렉토리·파일 (권장 분담 기준)

- `tools/data_tools.py` — `get_/create_/update_/delete_health_snapshot` (도메인 분담분)
- `data/health.json` — 데모 페르소나 컨디션 데이터
- `data/scenarios/*.json` — KPI 시나리오 운영 책임 (D와 공동 적재)
- `agent/prompts.py` 튜닝 — C와 협업
- `backend/api/data.py` — 자기 도메인 라우터(현재 501 stub)에 위임 채우기

## 합의 책임 (5/4 락)

- **C와**: Tool 시그니처 (LangGraph `@tool`로 래핑할 형태). schemas/models.py와 1:1
- **D와**: calendar/health/workouts 도메인 분담 + scenarios 운영 분담
- **A와**: `/data/*` REST 응답 형태 (= Tool 반환값 그대로)

## 일자별 to-do (권장 분담 기준)

| 날짜 | 할 일 | 합격 기준 |
|---|---|---|
| **5/4 (월)** | `data/health.json` 더미 5건 / `tools.get_health` 1차 구현 (JSON 파싱) | `pytest`에서 1주 범위 호출 시 비어있지 않은 리스트 |
| **5/5 (화)** | `get_health` JSON 실파싱 완성 / CRUD 중 첫 write 함수 (`create_health_snapshot`) | `POST /data/health`로 새 스냅샷 추가됨 |
| **5/6 (수)** | `update_/delete_health_snapshot` 일부 구현 / 1주치 더미 데이터 보강 (수면 부족 케이스) | 4종 CRUD 모두 200/204 응답 |
| **5/7 (목)** | `data/scenarios/`에 KPI 2(피로도 회피)·시나리오(수면 부족) 적재 | `data/scenarios/sleep_deprived.json` 등 파일 존재 |
| **5/8 (금)** ★ | write Tool 안정화 (atomic 파일 갱신) / 시나리오 데이터로 end-to-end 검증 | health 변경이 agent 응답에 반영됨 |
| **5/9 (토)** | 시나리오 입력 vs 기대 응답 매칭 정밀화 / 프롬프트 튜닝 (C와) | `pytest -m kpi` 2·4번 통과 |
| **5/10 (일)** | 데모용 health/scenarios 데이터 최종 점검 | 데모 시연 무사고 |

## KPI 시나리오 — 본인 영향

- **2번** 피로도 높음 회피 — health 데이터 + workouts 누적 (D와 공동)
- **4번** 멀티턴 재조정 — `data/scenarios/multiturn.json` 적재
- **수면 부족 시나리오** — 강도 하향 검증용

## 자주 볼 문서·CLAUDE.md

- `tools/CLAUDE.md` ← 본인 슬라이스 (CRUD 시그니처, atomic write)
- `data/CLAUDE.md` ← scenarios/ 구조 + 페르소나
- `schemas/CLAUDE.md` ← Pydantic 모델 (`HealthSnapshot`)
- `backend/CLAUDE.md` ← `/data/*` 라우터 위임 패턴
- `agent/CLAUDE.md` ← C가 어떻게 Tool을 호출하는지 (`@tool` 래퍼)

## 흔한 함정

- `tools/data_tools.py`는 D와 같이 만짐 → **함수 단위 PR**로 쪼갬 (PR 제목에 `[tools] create_health_snapshot 구현`)
- write는 read-modify-write — 동시성 걱정 없지만 atomic하게 (임시 파일 → `os.replace`)
- `resting_hr`은 옵셔널 — 없는 경우 처리
- 새 필드 추가는 `schemas/models.py` 먼저 수정 후 JSON 갱신
- 시나리오 운영(D와 공동) — 어떤 시나리오를 누가 책임지는지 데일리 싱크에서 명확히

# 43조 — 맞춤형 운동 스케줄링 에이전트

> 5인 팀 공유 컨텍스트. 이 파일 수정은 데일리 싱크 합의 후 PR로만.
> **각 디렉토리에 자체 `CLAUDE.md`가 있음** — 슬라이스별 디테일은 거기에서 본다.

**한 줄 정의**: 캘린더·건강·운동기록을 종합해 이번 주 맞춤 운동 스케줄을 자동 생성·재조정하는 LangGraph Agent + Flutter Web UI. 상세 기획·분담·일정은 [`docs/`](docs/CLAUDE.md) 참조 (분담 원본은 `docs/planning/plan.md`).

## 1. 팀 & 담당 슬라이스 (역할 분담)

| # | 슬라이스 | 담당 | 디렉토리·책임 |
|---|---|---|---|
| **A** | Flutter Web 프론트 (대시보드) | **노준영** | `frontend/` 전체. 좌측 카드 3종(일정/컨디션/최근 운동) + 가운데 부위별 피로도 레이더. BE와 `/data/*` REST 합의. |
| **B** | Chat UI + Agent 통신 프로토콜 | **박장우** | `frontend/lib/chat/` (FE 채팅, SSE 클라이언트, 디자인) + `backend/api/chat.py` 스펙 합의 (C와). Stream 구현. |
| **C** | LangGraph Agent (prompt + graph + memory) | **이유준** | `agent/`, `memory/`. `run_agent_stream` 진입점, FE 규격에 맞춘 SSE 청크 emit. |
| **D** | CRUD Tool + 시나리오·프롬프트 튜닝 | **박영준** | `tools/`, `data/` (도메인 분담은 데일리 싱크에서 E와) |
| **E** | CRUD Tool + 시나리오·프롬프트 튜닝 | **신승민** | `tools/`, `data/` (D와 동일 책임 영역) |

**Tech Lead**: C(이유준) 또는 D(박영준) — 매일 저녁 main 동작 확인 + 통합 책임. 5/4 데일리 싱크에서 확정.

**원칙**(`docs/planning/plan.md` 직역): "유저가 FE에서 보는 모든 데이터는 agent도 그대로 본다." → A의 화면에 뜨는 모든 항목에는 D/E가 read+write Tool을 노출.

## 2. 기술 스택

- **Backend**: Python 3.11+ / FastAPI / uvicorn / sse-starlette / LangGraph(+LangChain) / OpenAI GPT-4o / Pydantic v2
- **Frontend**: Flutter Web (Dart)
- **Datastore**: 로컬 JSON (`data/*.json`). 실제 Google Calendar/Apple Health API 미연동. `schemas/models.py`가 사실상 DB 스키마.
- **Agent 메모리**: LangGraph 체크포인터 (in-memory → 필요 시 SQLite)
- **의존성**: Python은 `requirements.txt`, Flutter는 `frontend/pubspec.yaml`. 추가 시 데일리 싱크 공지.

## 3. 레포 구조

```
AI_TECH_EDU/
├── frontend/    # A 노준영 (Flutter Web), B 박장우 (lib/chat/) → frontend/CLAUDE.md
├── backend/     # FastAPI 게이트웨이 (B/C/D/E 합의 지점) → backend/CLAUDE.md
│   ├── main.py
│   └── api/{data,chat}.py
├── agent/       # C 이유준 (LangGraph)        → agent/CLAUDE.md
├── memory/      # C 이유준 (체크포인터)       → memory/CLAUDE.md
├── tools/       # D 박영준 + E 신승민 (CRUD)  → tools/CLAUDE.md
├── data/        # D + E (가상 JSON + 시나리오) → data/CLAUDE.md
│   └── scenarios/
├── schemas/     # 전원 공유 (Pydantic 모델)   → schemas/CLAUDE.md
├── tests/       # 스모크/단위/KPI            → tests/CLAUDE.md
├── docs/        # 분담·일정·스펙·디자인       → docs/CLAUDE.md
│   ├── planning/  (plan.md, dev_plan.md, 킥오프_5월4일.md)
│   ├── spec/      (feature_spec.md, 프로젝트 기획서 양식_*.md)
│   └── design/    (flow.html, 메인 화면 PNG)
└── requirements.txt  .env.example
```

작업 시작 전 자기 슬라이스 디렉토리의 `CLAUDE.md`를 먼저 읽기.

## 4. 인터페이스 진입점 (자세한 모델은 `schemas/CLAUDE.md`)

```python
# tools/data_tools.py — D, E (read + write 모두)
get_calendar(start, end) -> list[CalendarEvent]
create_calendar_event(event) -> CalendarEvent
update_calendar_event(id, patch) -> CalendarEvent
delete_calendar_event(id) -> None
# health, workouts 동일 패턴

# agent/graph.py — C
async def run_agent_stream(user_input, thread_id) -> AsyncIterator[ChatChunk]
# (비스트림 run_agent도 보존 — 테스트·단순 호출용)

# backend/api/ — FastAPI 라우터 (얇은 위임)
GET    /data/calendar?start&end       -> list[CalendarEvent]
POST   /data/calendar                  -> CalendarEvent
PATCH  /data/calendar/{id}             -> CalendarEvent
DELETE /data/calendar/{id}             -> 204
# health, workouts 동일

POST   /agent/chat   (SSE)             -> stream of ChatChunk
GET    /health                          -> ping
```

위 시그니처는 **5/4 킥오프에서 락**. 변경 절차는 `schemas/CLAUDE.md` 참고.

## 5. 협업 규칙

- **Git**: `main` 보호, 브랜치 `feat/<A~E>-<짧은설명>`, PR은 함수/엔드포인트 단위로 작게, 리뷰어 1명 이상 승인 후 머지(셀프 머지 금지). 같은 파일(`tools/data_tools.py`, `backend/api/data.py`)을 여럿이 만질 땐 싱크에서 머지 순서 정함.
- **Mock-first**: 데이터/타 슬라이스 함수가 없어도 `schemas/` 더미와 `NotImplementedError` / `501` stub으로 작업 시작. 실제 LLM 호출은 5/8 통합 전까지 stub 가능.
- **데일리 15분 싱크**: 어제/오늘/막힌 것. 인터페이스 변경 논의는 이 자리에서만.
- **시크릿**: `.env` 절대 커밋 금지(`.gitignore` 등록), 새 변수는 `.env.example`에 키만 추가.

## 6. 코딩 컨벤션

타입 힌트 필수. UI/챗 응답은 한국어, 코드·주석·식별자는 영어. 주석은 *왜*가 비자명할 때만. LangGraph 노드는 한 가지 일만. **외부 LLM 호출은 `agent/nodes.py` 한 곳에 모음**(다른 모듈 직접 호출 금지). FastAPI 라우터는 비즈니스 로직 금지(검증·직렬화·에러 매핑만, 실제 일은 `tools/`/`agent/`).

## 7. 환경 셋업

```bash
# Backend (Python)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # OPENAI_API_KEY 채우기
uvicorn backend.main:app --reload      # http://localhost:8000/docs (Swagger)
pytest

# Frontend (Flutter Web — A가 5/5에 셋업)
cd frontend
flutter create .
flutter run -d chrome
```

## 8. 일정 (2026-05-04 ~ 05-10, 코드 동결)

| 날짜          | 마일스톤                                       |
| ----------- | ------------------------------------------ |
| 5/4 (월)     | 인터페이스 락(REST + SSE 청크 + Tool 시그니처), 레포 재편, LangGraph 튜토리얼 1시간 페어 학습 |
| 5/5 (화)     | A `flutter create` + 카드 1종, B 채팅 셸, C agent stub 그래프 1회 실행, D/E CRUD 첫 함수 |
| 5/6 (수)     | 핵심 로직 (1주치 데이터, Tool 연결, 스케줄 도출)           |
| 5/7 (목)     | 멀티턴 메모리, 재조정 흐름                            |
| **5/8 (금)** | **★ 1차 통합 — Flutter ↔ FastAPI ↔ Agent end-to-end 1회 성공** |
| 5/9 (토)     | 통합 테스트, KPI 시나리오 5개, 엣지 케이스                |
| 5/10 (일)    | **코드 동결**, 데모 시나리오 무사고 시연, 태그 `v1.0-demo`  |

발표일: **2026-05-15(금)**. 5/11~14는 발표 자료·리허설.

## 9. KPI 시나리오 (5/9 통과 목표)

1. 일정 충돌률 1% 미만 (10회 생성 시 충돌 0회)
2. 피로도 "높음" 부위에 해당 부위 운동 추천 0회
3. 빈 시간 없는 주에 10분 대체 루틴(홈트·계단) 제안
4. 멀티턴 재조정 ("화요일은 피곤할 것 같아") → 해당 일자만 변경
5. 추천 부위와 FE 레이더 차트 색상 변화 일치

각 시나리오 입력은 `data/scenarios/*.json`에서 관리 (D/E).

## 10. 절대 하지 말 것

- 실제 Google Calendar / Apple Health API 연동 (MVP 범위 외)
- `.env`·API 키 커밋, `main` 직접 push, 셀프 머지
- `schemas/models.py`·Tool 시그니처·API 엔드포인트를 단독 결정으로 변경
- 다른 슬라이스 디렉토리를 합의 없이 리팩터링
- 사용자에게 보여줄 메시지를 영어로 작성
- FastAPI 라우터에서 OpenAI 직접 호출 (전부 `agent/nodes.py` 경유)

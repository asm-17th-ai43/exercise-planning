# backend/ — FastAPI 게이트웨이

> **담당**: 라우터 분담 — `data.py`는 D(박영준)+E(신승민), `chat.py`는 B(박장우)+C(이유준).

## 역할

Flutter Web 프론트(A 노준영)와 LangGraph Agent 사이의 HTTP 게이트웨이. 데이터는 REST CRUD, 챗은 SSE 스트림.

## 엔드포인트

| Method | Path | 책임 슬라이스 | 비고 |
|---|---|---|---|
| GET | `/data/calendar?start&end` | D/E | `tools.get_calendar` 위임 |
| POST | `/data/calendar` | D/E | `tools.create_calendar_event` |
| PATCH | `/data/calendar/{id}` | D/E | `tools.update_calendar_event` |
| DELETE | `/data/calendar/{id}` | D/E | `tools.delete_calendar_event` |
| GET/POST/PATCH/DELETE | `/data/health` · `/data/workouts` | D/E | 동일 패턴 |
| POST | `/agent/chat` (SSE) | B/C | `agent.run_agent_stream` → `ChatChunk` 시퀀스 |
| GET | `/health` | — | 부팅 확인 ping |

## 합의 포인트 (이미 락)

- **`ChatChunk.type`별 payload**: 이미 schemas/CLAUDE.md 표에 박힘:
  - `text`: `{ "delta": "응답 토큰 일부" }`
  - `tool_call`: `{ "name": "get_calendar", "args": {...} }`
  - `proposal`: `ScheduleProposal.model_dump(mode="json")`
  - `done`: `{ "thread_id": "..." }`
  - `error`: `{ "message": "..." }`
- **CRUD 시그니처**: D/E가 tools/data_tools.py에 정의하는 함수가 라우터의 진실 (라우터는 얇은 위임).
- **CORS**: 개발 중엔 `localhost:*` 허용. 데모 도메인이 정해지면 origin 화이트리스트 갱신.
- **변경 필요 시**: PR 제목에 `[interface-change]` 태그 + 5명 react 후 머지.

## 실행

```bash
uvicorn backend.main:app --reload
# Swagger: http://localhost:8000/docs
```

## 작업 시 주의

- 라우터 핸들러는 **얇게**. 비즈니스 로직은 `tools/`, `agent/`에. 라우터는 검증·직렬화·에러 매핑만.
- `from schemas.models import ...` 사용. 라우터에서 새 모델 정의 금지.
- 새 엔드포인트는 `[interface-change]` PR로만 추가. FE(A)가 모르는 엔드포인트는 만들지 말기.
- 실제 LLM 호출은 `agent/nodes.py` 한 곳에서만 (`backend/api/chat.py`에서 OpenAI 직접 호출 금지).

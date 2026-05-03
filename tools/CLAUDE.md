# tools/ — LangGraph Tool (데이터 조회)

> **담당**: #1 `get_calendar` · #2 `get_health` · #3 `get_workouts`
> 같은 파일(`data_tools.py`)을 셋이 만지므로 **함수 단위 PR**로 쪼개기.

## 시그니처 (락)

```python
def get_calendar(start: date, end: date) -> list[CalendarEvent]: ...
def get_health(start: date, end: date) -> list[HealthSnapshot]: ...
def get_workouts(start: date, end: date) -> list[WorkoutRecord]: ...
```

`[start, end]`는 양 끝 포함. JSON 파일은 `data/`에서 읽는다.

## 구현 가이드

- 파일 경로는 `pathlib.Path(__file__).parent.parent / "data" / "..."` 같은 상대 위치로 (CWD 의존 X)
- 파싱은 Pydantic의 `Model.model_validate(dict)` 사용 — 타입 안전
- 빈 결과는 빈 리스트 `[]`. None 반환 금지.
- 날짜 비교는 `event.start.date()` 같이 `date` 타입으로 통일

## LangGraph Tool 등록

5/6 이후 LangGraph 노드에서 호출할 때는 `@tool` 데코레이터로 감싼 래퍼를 별도로 둔다:

```python
from langchain_core.tools import tool

@tool
def calendar_tool(start: str, end: str) -> list[dict]:
    """이번 주 사용자 캘린더를 조회한다."""
    events = get_calendar(date.fromisoformat(start), date.fromisoformat(end))
    return [e.model_dump(mode="json") for e in events]
```

순수 함수(`get_calendar`)와 LLM용 래퍼(`calendar_tool`)는 **반드시 분리**. 테스트는 순수 함수 기준으로 작성.

## 협업 룰

- PR 제목에 `[tools] get_xxx 구현` 식으로 자기 함수 명시
- 같은 파일 동시 수정이 필요한 PR이 두 개 이상이면 데일리 싱크에서 머지 순서 확정
- import 추가는 알파벳 정렬 유지

"""LangGraph @tool 래퍼. 순수 함수(tools/data_tools.py)와 LLM 인터페이스를 분리."""
from datetime import date

from langchain_core.tools import tool

from tools.data_tools import create_calendar_event as _create_calendar_event
from tools.data_tools import create_workout as _create_workout
from tools.data_tools import delete_calendar_event as _delete_calendar_event
from tools.data_tools import delete_workout as _delete_workout
from tools.data_tools import get_calendar as _get_calendar
from tools.data_tools import get_health as _get_health
from tools.data_tools import get_workouts as _get_workouts
from tools.data_tools import update_calendar_event as _update_calendar_event
from tools.data_tools import update_workout as _update_workout
from schemas.models import CalendarEvent, WorkoutRecord


# ── Read ────────────────────────────────────────────────────────────────────

@tool
def calendar_tool(start: str, end: str) -> list[dict]:
    """이번 주 사용자 캘린더 일정을 조회한다. start/end는 YYYY-MM-DD 형식."""
    try:
        events = _get_calendar(date.fromisoformat(start), date.fromisoformat(end))
        return [e.model_dump(mode="json") for e in events]
    except Exception:
        # D/E 미구현 또는 Supabase 미연결 시 빈 리스트로 파이프라인 유지
        return []


@tool
def health_tool(start: str, end: str) -> list[dict]:
    """최근 수면 시간·활동량·안정 심박수를 조회한다. start/end는 YYYY-MM-DD 형식."""
    try:
        snapshots = _get_health(date.fromisoformat(start), date.fromisoformat(end))
        return [s.model_dump(mode="json") for s in snapshots]
    except Exception:
        return []


@tool
def workouts_tool(start: str, end: str) -> list[dict]:
    """최근 운동 기록과 부위별 피로도를 조회한다. start/end는 YYYY-MM-DD 형식."""
    try:
        records = _get_workouts(date.fromisoformat(start), date.fromisoformat(end))
        return [r.model_dump(mode="json") for r in records]
    except Exception:
        return []


# ── Write — Calendar ─────────────────────────────────────────────────────────

@tool
def create_calendar_event_tool(event: dict) -> dict:
    """캘린더 이벤트 1건을 추가하고 생성된 이벤트를 반환한다.

    event 필드: title(str), start_at(ISO datetime), end_at(ISO datetime),
    event_type(str, optional), description(str, optional).
    """
    created = _create_calendar_event(CalendarEvent.model_validate(event))
    return created.model_dump(mode="json")


@tool
def update_calendar_event_tool(event_id: str, patch: dict) -> dict:
    """캘린더 이벤트를 부분 수정하고 수정된 이벤트를 반환한다.

    event_id: 수정할 이벤트의 UUID.
    patch: 변경할 필드만 포함 (예: {"title": "새 제목", "start_at": "2026-05-06T10:00:00"}).
    재조정 시 기존 이벤트를 덮어쓸 때 사용한다.
    """
    updated = _update_calendar_event(event_id, patch)
    return updated.model_dump(mode="json")


@tool
def delete_calendar_event_tool(event_id: str) -> dict:
    """캘린더 이벤트 1건을 삭제한다.

    event_id: 삭제할 이벤트의 UUID.
    재조정 시 해당 날짜 기존 이벤트를 지운 뒤 새 이벤트를 생성한다.
    """
    _delete_calendar_event(event_id)
    return {"deleted": event_id}


# ── Write — Workouts ─────────────────────────────────────────────────────────

@tool
def create_workout_tool(record: dict) -> dict:
    """운동 기록 1건을 추가하고 생성된 기록을 반환한다.

    record 필드: date(YYYY-MM-DD), workout_type(str), duration_minutes(int),
    muscles(list[str]), intensity(str, optional).
    """
    created = _create_workout(WorkoutRecord.model_validate(record))
    return created.model_dump(mode="json")


@tool
def update_workout_tool(record_id: str, patch: dict) -> dict:
    """운동 기록을 부분 수정하고 수정된 기록을 반환한다.

    record_id: 수정할 기록의 UUID.
    patch: 변경할 필드만 포함.
    """
    updated = _update_workout(record_id, patch)
    return updated.model_dump(mode="json")


@tool
def delete_workout_tool(record_id: str) -> dict:
    """운동 기록 1건을 삭제한다.

    record_id: 삭제할 기록의 UUID.
    """
    _delete_workout(record_id)
    return {"deleted": record_id}

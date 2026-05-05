"""데이터 조회·변경 Tool.

담당:
- D(박영준): calendar + workouts CRUD 8개
- E(신승민): health CRUD 4개

유저가 FE에서 보는 모든 데이터는 agent도 그대로 본다 — 그러므로 read+write 둘 다.
같은 파일을 둘이 만지므로 PR을 함수 단위로 잘게 쪼갤 것.
"""
import os
from datetime import date

from dotenv import load_dotenv
from supabase import Client, create_client

from schemas.models import CalendarEvent, HealthSnapshot, WorkoutRecord

load_dotenv()


def _client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])


# ---------- Calendar ----------
def get_calendar(start: date, end: date) -> list[CalendarEvent]:
    """[start, end] 범위 내 start_at을 가진 캘린더 이벤트 반환."""
    rows = (
        _client()
        .table("calendar_events")
        .select("*")
        .gte("start_at", f"{start}T00:00:00")
        .lte("start_at", f"{end}T23:59:59")
        .execute()
    )
    return [CalendarEvent.model_validate(row) for row in rows.data]


def create_calendar_event(event: CalendarEvent) -> CalendarEvent:
    """이벤트 1건 추가. id 채번 후 반환."""
    data = event.model_dump(mode="json", exclude={"id"})
    row = _client().table("calendar_events").insert(data).execute()
    return CalendarEvent.model_validate(row.data[0])


def update_calendar_event(event_id: str, patch: dict) -> CalendarEvent:
    """이벤트 부분 수정. 갱신된 이벤트 반환."""
    raise NotImplementedError("D/E 합의 후 구현")


def delete_calendar_event(event_id: str) -> None:
    """이벤트 1건 삭제."""
    raise NotImplementedError("D/E 합의 후 구현")


# ---------- Health ----------
def get_health(start: date, end: date) -> list[HealthSnapshot]:
    """data/health.json을 읽어 [start, end] 범위 스냅샷 반환."""
    raise NotImplementedError("D/E 합의 후 구현")


def create_health_snapshot(snapshot: HealthSnapshot) -> HealthSnapshot:
    """스냅샷 1건 추가."""
    raise NotImplementedError("D/E 합의 후 구현")


def update_health_snapshot(snapshot_date: date, patch: dict) -> HealthSnapshot:
    """해당 일자 스냅샷 부분 수정."""
    raise NotImplementedError("D/E 합의 후 구현")


def delete_health_snapshot(snapshot_date: date) -> None:
    """해당 일자 스냅샷 삭제."""
    raise NotImplementedError("D/E 합의 후 구현")


# ---------- Workouts ----------
def get_workouts(start: date, end: date) -> list[WorkoutRecord]:
    """[start, end] 범위 운동 기록 반환."""
    rows = (
        _client()
        .table("workout_records")
        .select("*")
        .gte("date", start.isoformat())
        .lte("date", end.isoformat())
        .execute()
    )
    return [WorkoutRecord.model_validate(row) for row in rows.data]


def create_workout(record: WorkoutRecord) -> WorkoutRecord:
    """운동 기록 1건 추가."""
    raise NotImplementedError("D/E 합의 후 구현")


def update_workout(record_id: str, patch: dict) -> WorkoutRecord:
    """운동 기록 부분 수정."""
    raise NotImplementedError("D/E 합의 후 구현")


def delete_workout(record_id: str) -> None:
    """운동 기록 1건 삭제."""
    raise NotImplementedError("D/E 합의 후 구현")

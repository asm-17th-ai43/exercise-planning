"""데이터 조회·변경 Tool. 담당: D(박영준) + E(신승민).

유저가 FE에서 보는 모든 데이터는 agent도 그대로 본다 — 그러므로 read+write 둘 다.
같은 파일을 둘이 만지므로 PR을 함수 단위로 잘게 쪼갤 것.
D-E의 도메인 분담(예: D=calendar/workouts, E=health/scenarios)은 데일리 싱크에서 결정.
"""
from datetime import date

from schemas.models import CalendarEvent, HealthSnapshot, WorkoutRecord


# ---------- Calendar ----------
def get_calendar(start: date, end: date) -> list[CalendarEvent]:
    """data/calendar.json을 읽어 [start, end] 범위 이벤트 반환."""
    raise NotImplementedError("D/E 합의 후 구현")


def create_calendar_event(event: CalendarEvent) -> CalendarEvent:
    """이벤트 1건 추가. id 채번 후 반환."""
    raise NotImplementedError("D/E 합의 후 구현")


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
    """data/workouts.json을 읽어 [start, end] 범위 운동 기록 반환."""
    raise NotImplementedError("D/E 합의 후 구현")


def create_workout(record: WorkoutRecord) -> WorkoutRecord:
    """운동 기록 1건 추가."""
    raise NotImplementedError("D/E 합의 후 구현")


def update_workout(record_id: str, patch: dict) -> WorkoutRecord:
    """운동 기록 부분 수정."""
    raise NotImplementedError("D/E 합의 후 구현")


def delete_workout(record_id: str) -> None:
    """운동 기록 1건 삭제."""
    raise NotImplementedError("D/E 합의 후 구현")

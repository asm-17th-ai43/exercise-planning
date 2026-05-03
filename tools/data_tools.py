"""데이터 조회 Tool. 담당: #1(calendar), #2(health), #3(workouts).

각자 자기 함수를 구현하면서 같은 파일을 만지므로 PR을 함수 단위로 잘게 쪼갤 것.
"""
from datetime import date

from schemas import CalendarEvent, HealthSnapshot, WorkoutRecord


def get_calendar(start: date, end: date) -> list[CalendarEvent]:
    """담당: #1. data/calendar.json을 읽어 [start, end] 범위 이벤트 반환."""
    raise NotImplementedError("담당: #1 캘린더 슬라이스")


def get_health(start: date, end: date) -> list[HealthSnapshot]:
    """담당: #2. data/health.json을 읽어 [start, end] 범위 스냅샷 반환."""
    raise NotImplementedError("담당: #2 건강 슬라이스")


def get_workouts(start: date, end: date) -> list[WorkoutRecord]:
    """담당: #3. data/workouts.json을 읽어 [start, end] 범위 운동 기록 반환."""
    raise NotImplementedError("담당: #3 운동기록 슬라이스")

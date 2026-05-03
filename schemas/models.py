"""공통 데이터 모델. 변경은 데일리 싱크 합의 후에만."""
from datetime import date, datetime

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    start: datetime
    end: datetime
    title: str
    is_busy: bool = True


class HealthSnapshot(BaseModel):
    date: date
    sleep_hours: float
    activity_minutes: int
    resting_hr: int | None = None


class WorkoutRecord(BaseModel):
    date: date
    type: str
    duration_min: int
    muscles: list[str]
    intensity: int = Field(ge=1, le=5)


class WorkoutSlot(BaseModel):
    start: datetime
    end: datetime
    type: str
    target_muscles: list[str]
    intensity: int = Field(ge=1, le=5)
    rationale: str


class MuscleFatigueState(BaseModel):
    date: date
    fatigue: dict[str, int]  # 부위명 → 0~5


class ScheduleProposal(BaseModel):
    slots: list[WorkoutSlot]
    fatigue_timeline: list[MuscleFatigueState]


class AgentResponse(BaseModel):
    message: str
    proposal: ScheduleProposal | None = None
    needs_approval: bool = False

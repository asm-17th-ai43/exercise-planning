"""LangGraph 노드 정의. 담당: C(이유준).

ReAct 패턴: 1) 일정 확인 → 2) 건강 확인 → 3) 운동 기록 확인 → 스케줄 도출.
외부 LLM 호출은 이 파일 안에 모은다(다른 모듈에서 직접 OpenAI 호출 금지).
"""
from __future__ import annotations

import datetime

from schemas.models import MuscleFatigueState, ScheduleProposal, WorkoutSlot

_REACT_STEPS = ["get_calendar", "get_health", "get_workouts"]

# feature_spec F5: 부위 7종
_MUSCLES = ["가슴", "등", "하체", "어깨", "코어", "이두", "삼두"]

_WORKOUT_HOUR_START = 6   # 06:00 이후 운동 가능
_WORKOUT_HOUR_END = 22    # 22:00 이전 운동 가능
_MIN_SLOT_MIN = 30        # 30분 미만 창은 무시
_DEFAULT_DURATION_MIN = 60


def _this_week_range() -> tuple[str, str]:
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday())
    end = start + datetime.timedelta(days=6)
    return start.isoformat(), end.isoformat()


# ── 스케줄 도출 헬퍼 ──────────────────────────────────────────────────────────

def _compute_muscle_fatigue(workouts: list[dict]) -> dict[str, float]:
    """최근 7일 운동 기록으로 부위별 피로도(0~5)를 계산한다."""
    today = datetime.date.today()
    fatigue: dict[str, float] = {m: 0.0 for m in _MUSCLES}
    for w in workouts:
        try:
            workout_date = datetime.date.fromisoformat(w["date"])
        except (KeyError, ValueError):
            continue
        days_ago = (today - workout_date).days
        if days_ago > 7:
            continue
        # 최근일수록 피로가 많이 남아있음
        decay = max(0.0, (7 - days_ago) / 7)
        intensity = w.get("intensity", 3)
        for muscle in w.get("muscles", []):
            if muscle in fatigue:
                fatigue[muscle] = min(5.0, fatigue[muscle] + intensity * decay)
    return {m: round(v, 1) for m, v in fatigue.items()}


def _assess_condition(health: list[dict]) -> dict:
    """건강 데이터로 컨디션을 평가한다."""
    if not health:
        return {"avg_sleep": 7.0, "avg_activity": 40, "fatigue_flag": False}
    avg_sleep = sum(h.get("sleep_hours", 7.0) for h in health) / len(health)
    avg_activity = sum(h.get("activity_minutes", 30) for h in health) / len(health)
    return {
        "avg_sleep": round(avg_sleep, 1),
        "avg_activity": round(avg_activity),
        "fatigue_flag": avg_sleep < 5.5,
    }


def _busy_intervals(
    calendar: list[dict], target_date: datetime.date
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """특정 날짜의 is_busy=True 구간을 시작 시각 순으로 반환한다."""
    intervals = []
    for ev in calendar:
        if not ev.get("is_busy", True):
            continue
        try:
            start = datetime.datetime.fromisoformat(ev["start_at"])
            end = datetime.datetime.fromisoformat(ev["end_at"])
        except (KeyError, ValueError):
            continue
        if start.date() == target_date:
            intervals.append((start, end))
    return sorted(intervals, key=lambda x: x[0])


def _find_free_windows(
    busy: list[tuple[datetime.datetime, datetime.datetime]],
    target_date: datetime.date,
) -> list[tuple[datetime.datetime, datetime.datetime]]:
    """하루 중 _MIN_SLOT_MIN 이상의 빈 시간 창을 반환한다."""
    day_start = datetime.datetime(target_date.year, target_date.month, target_date.day, _WORKOUT_HOUR_START, 0)
    day_end = datetime.datetime(target_date.year, target_date.month, target_date.day, _WORKOUT_HOUR_END, 0)

    free = []
    cursor = day_start
    for b_start, b_end in busy:
        b_start = max(b_start, day_start)
        b_end = min(b_end, day_end)
        if cursor < b_start:
            gap_min = (b_start - cursor).total_seconds() / 60
            if gap_min >= _MIN_SLOT_MIN:
                free.append((cursor, b_start))
        cursor = max(cursor, b_end)
    if cursor < day_end:
        gap_min = (day_end - cursor).total_seconds() / 60
        if gap_min >= _MIN_SLOT_MIN:
            free.append((cursor, day_end))
    return free


def _select_workout(
    fatigue: dict[str, float], condition: dict, slot_min: int
) -> tuple[str, list[str], int, str]:
    """피로도·컨디션 기반으로 (운동유형, 대상부위, 강도, 설명)을 결정한다."""
    base_intensity = 2 if condition["fatigue_flag"] else 3

    if slot_min < 20:
        return ("홈트", ["코어"], max(1, base_intensity - 1), "짧은 시간 → 코어 홈트")

    # 피로도 낮은 부위 우선 선택 (KPI #2: 피로도 높은 부위 회피)
    high_fatigue = [m for m, f in fatigue.items() if f >= 4.0]
    eligible = [m for m in _MUSCLES if fatigue.get(m, 0) < 4.0]

    if not eligible:
        return ("러닝", ["하체", "코어"], base_intensity, "전신 피로 → 유산소 권장")

    sorted_eligible = sorted(eligible, key=lambda m: fatigue.get(m, 0))
    target = sorted_eligible[:2]

    resistance = {"가슴", "등", "어깨", "이두", "삼두"}
    if any(m in resistance for m in target):
        workout_type = "헬스"
    elif "하체" in target and slot_min >= 35:
        workout_type = "러닝"
    else:
        workout_type = "홈트"

    rationale = f"피로도 낮은 부위({', '.join(target)}) / 수면 {condition['avg_sleep']}h"
    if high_fatigue:
        rationale += f" / {', '.join(high_fatigue)} 회피"

    return (workout_type, target, base_intensity, rationale)


# ── 노드 함수 ────────────────────────────────────────────────────────────────

def think_node(state: dict) -> dict:
    """다음에 호출할 Tool을 결정한다.

    5/5 stub: LLM 없이 하드코딩된 ReAct 순서. 5/8에 실제 LLM 판단으로 교체.
    """
    called: list[str] = state.get("tools_called", [])
    for step in _REACT_STEPS:
        if step not in called:
            return {"next_action": step}
    return {"next_action": "compose"}


def call_tool_node(state: dict) -> dict:
    """next_action에 해당하는 Tool을 호출하고 결과를 state에 저장한다."""
    from agent.tools import calendar_tool, health_tool, workouts_tool

    action: str = state["next_action"]
    start, end = _this_week_range()
    called: list[str] = list(state.get("tools_called", []))

    if action == "get_calendar":
        data = calendar_tool.invoke({"start": start, "end": end})
        called.append("get_calendar")
        return {"calendar_data": data, "tools_called": called}

    if action == "get_health":
        data = health_tool.invoke({"start": start, "end": end})
        called.append("get_health")
        return {"health_data": data, "tools_called": called}

    if action == "get_workouts":
        data = workouts_tool.invoke({"start": start, "end": end})
        called.append("get_workouts")
        return {"workouts_data": data, "tools_called": called}

    return {}


def compose_schedule_node(state: dict) -> dict:
    """수집한 데이터로 이번 주 ScheduleProposal을 생성한다."""
    calendar: list[dict] = state.get("calendar_data", [])
    health: list[dict] = state.get("health_data", [])
    workouts: list[dict] = state.get("workouts_data", [])

    fatigue = _compute_muscle_fatigue(workouts)
    condition = _assess_condition(health)

    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())

    slots: list[WorkoutSlot] = []
    # 주간 피로도 누적 추적 (제안된 운동 반영)
    running_fatigue = dict(fatigue)

    for day_offset in range(7):
        target_date = week_start + datetime.timedelta(days=day_offset)
        busy = _busy_intervals(calendar, target_date)
        free_windows = _find_free_windows(busy, target_date)

        if not free_windows:
            # KPI #3: 빈 시간 0 → 10분 대체 루틴
            alt_start = datetime.datetime(
                target_date.year, target_date.month, target_date.day, 7, 0
            )
            slots.append(WorkoutSlot(
                start=alt_start,
                end=alt_start + datetime.timedelta(minutes=10),
                type="홈트",
                target_muscles=["코어"],
                intensity=1,
                rationale="빈 시간 없음 → 10분 대체 루틴 (계단·스트레칭)",
            ))
            continue

        # 첫 번째 빈 창에 하루 1회 운동 배치
        window_start, window_end = free_windows[0]
        avail_min = int((window_end - window_start).total_seconds() / 60)
        duration_min = min(_DEFAULT_DURATION_MIN, avail_min)
        slot_end = window_start + datetime.timedelta(minutes=duration_min)

        workout_type, target_muscles, intensity, rationale = _select_workout(
            running_fatigue, condition, duration_min
        )

        slots.append(WorkoutSlot(
            start=window_start,
            end=slot_end,
            type=workout_type,
            target_muscles=target_muscles,
            intensity=intensity,
            rationale=rationale,
        ))

        # 제안 운동 후 피로도 업데이트
        for m in target_muscles:
            running_fatigue[m] = min(5.0, running_fatigue.get(m, 0.0) + intensity * 0.5)

    # 이번 주 일별 피로도 타임라인 (초기값 기준 — 제안 전 상태)
    fatigue_timeline = [
        MuscleFatigueState(
            date=week_start + datetime.timedelta(days=i),
            fatigue={m: int(min(5, round(fatigue[m]))) for m in _MUSCLES},
        )
        for i in range(7)
    ]

    proposal = ScheduleProposal(slots=slots, fatigue_timeline=fatigue_timeline)
    return {"proposal": proposal.model_dump(mode="json")}


def refine_node(state: dict) -> dict:
    """멀티턴 재조정 노드. 5/7 구현 예정."""
    raise NotImplementedError("5/7 구현 예정")

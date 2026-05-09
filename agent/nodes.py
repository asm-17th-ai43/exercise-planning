"""LangGraph 노드 정의. 담당: C(이유준).

ReAct 패턴: 1) 일정 확인 → 2) 건강 확인 → 3) 운동 기록 확인 → 스케줄 도출.
외부 LLM 호출은 이 파일 안에 모은다(다른 모듈에서 직접 OpenAI 호출 금지).
"""
from __future__ import annotations

import datetime
from collections.abc import AsyncIterator

from schemas.models import MuscleFatigueState, ScheduleProposal, WorkoutSlot

# 요일 키워드 → weekday 번호 (0=월, 6=일). 긴 문자열 우선 매칭.
_DAY_KEYWORDS: dict[str, int] = {
    "월요일": 0, "화요일": 1, "수요일": 2, "목요일": 3,
    "금요일": 4, "토요일": 5, "일요일": 6,
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
    "월": 0, "화": 1, "수": 2, "목": 3, "금": 4, "토": 5, "일": 6,
}

_REACT_STEPS = ["get_calendar", "get_health", "get_workouts"]

# feature_spec F5: 부위 7종
_MUSCLES = ["가슴", "등", "하체", "어깨", "코어", "이두", "삼두"]

_KST = datetime.timezone(datetime.timedelta(hours=9))

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

def _compute_proposal_fatigue(
    slots: list,  # list[WorkoutSlot]
    before_date: datetime.date,
) -> dict[str, float]:
    """제안된 슬롯 중 before_date 이전 슬롯들의 누적 피로도를 계산한다.

    compose_schedule_node의 running_fatigue와 동일한 가중치(intensity * 0.5)를 사용해
    refine_node에서도 이미 제안된 슬롯의 부위 피로도를 반영한다.
    """
    fatigue: dict[str, float] = {m: 0.0 for m in _MUSCLES}
    for slot in slots:
        if slot.start.date() >= before_date:
            continue
        for m in slot.target_muscles:
            if m in fatigue:
                fatigue[m] = min(5.0, fatigue[m] + slot.intensity * 0.5)
    return fatigue


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
            start = datetime.datetime.fromisoformat(ev["start_at"]).astimezone(_KST).replace(tzinfo=None)
            end = datetime.datetime.fromisoformat(ev["end_at"]).astimezone(_KST).replace(tzinfo=None)
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


def _parse_user_intent(user_input: str) -> dict:
    """사용자 입력에서 운동 의도를 파싱한다.

    반환 키:
      restrict_muscles: list[str] | None  — 이 부위만 사용 ("X만", "X 집중")
      force_rest: bool                    — 가볍게 쉬기 요청
      intensity_cap: int | None           — 최대 강도 제한
    """
    text = user_input.lower()

    rest_kw = ["쉬게", "쉬고 싶", "쉬어", "휴식", "아무것도", "운동 하지 말", "운동하지 말", "쉬자"]
    force_rest = any(k in text for k in rest_kw)

    mentioned = [m for m in _MUSCLES if m in text]

    restrict_muscles: list[str] | None = None
    if mentioned and not force_rest:
        restrict_kw = ["집중", "위주", "만 하", "만해", "만 해"]
        has_restrict = any(k in text for k in restrict_kw)
        if not has_restrict:
            for m in mentioned:
                if f"{m}만" in text or f"{m} 만" in text:
                    has_restrict = True
                    break
        if has_restrict:
            restrict_muscles = mentioned

    intensity_cap: int | None = None
    if any(k in text for k in ["피곤", "힘들", "무리", "살살", "가볍게", "쉽게", "지쳐"]):
        intensity_cap = 2
    if force_rest:
        intensity_cap = 1

    return {
        "restrict_muscles": restrict_muscles,
        "force_rest": force_rest,
        "intensity_cap": intensity_cap,
    }


def _select_workout(
    fatigue: dict[str, float],
    condition: dict,
    slot_min: int,
    excluded_muscles: frozenset[str] = frozenset(),
    user_intent: dict | None = None,
) -> tuple[str, list[str], int, str]:
    """피로도·컨디션·사용자 의도 기반으로 (운동유형, 대상부위, 강도, 설명)을 결정한다.

    excluded_muscles: refine 시 현재 슬롯 부위를 넘겨 다른 선택을 강제한다.
    user_intent: _parse_user_intent() 결과. None이면 의도 없음으로 처리.
    """
    intent = user_intent or {}
    base_intensity = 2 if condition["fatigue_flag"] else 3

    if intent.get("intensity_cap") is not None:
        base_intensity = min(base_intensity, intent["intensity_cap"])

    if intent.get("force_rest"):
        return ("휴식", ["코어"], 1, "사용자 요청: 가볍게 쉬는 날")

    if slot_min < 20:
        return ("홈트", ["코어"], max(1, base_intensity - 1), "짧은 시간 → 코어 홈트")

    # 피로도 낮은 부위 우선 선택 (KPI #2: 피로도 높은 부위 회피)
    high_fatigue = [m for m, f in fatigue.items() if f >= 4.0]

    restrict = intent.get("restrict_muscles")
    candidate_pool = restrict if restrict else _MUSCLES
    eligible = [
        m for m in candidate_pool
        if fatigue.get(m, 0) < 4.0 and m not in excluded_muscles
    ]

    # 사용자 지정 부위가 모두 피로도 초과면 고피로 제외 없이 재시도
    if not eligible and restrict:
        eligible = [m for m in restrict if m not in excluded_muscles]

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
    if restrict:
        rationale += f" / 사용자 요청: {', '.join(restrict)} 위주"

    return (workout_type, target, base_intensity, rationale)


# ── 노드 함수 ────────────────────────────────────────────────────────────────

def _parse_target_weekday(text: str) -> int | None:
    """사용자 입력에서 요일을 파싱해 weekday 번호(0=월, 6=일)를 반환. 없으면 None."""
    text_lower = text.lower()
    for keyword in sorted(_DAY_KEYWORDS, key=len, reverse=True):
        if keyword in text_lower:
            return _DAY_KEYWORDS[keyword]
    return None


def think_node(state: dict) -> dict:
    """다음에 호출할 Tool을 결정한다.

    mode=="refine"이면 refine 노드로 보내고,
    그 외에는 get_calendar → get_health → get_workouts → compose 고정 순서로 진행.
    LLM 판단은 항상 동일한 순서를 반환하므로 hardcoded로 유지 (응답 속도 최적화).
    """
    if state.get("mode") == "refine":
        return {"next_action": "refine"}

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
    user_intent = _parse_user_intent(state.get("user_input", ""))

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
            running_fatigue, condition, duration_min, user_intent=user_intent
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


def _format_slots(slots: list[dict]) -> str:
    """슬롯 목록을 LLM 프롬프트용 텍스트로 변환한다."""
    lines = []
    for s in slots:
        date_str = s["start"][:10]
        time_str = f"{s['start'][11:16]}~{s['end'][11:16]}"
        muscles = ", ".join(s.get("target_muscles", []))
        rationale = s.get("rationale", "")
        lines.append(f"- {date_str} {time_str}: {s['type']} ({muscles}) — {rationale}")
    return "\n".join(lines)


async def generate_proposal_summary(
    proposal: dict,
    user_input: str,
    api_key: str,
    is_refine: bool = False,
    prior_proposal: dict | None = None,
) -> AsyncIterator[str]:
    """제안된 스케줄을 한국어 텍스트로 토큰 단위로 스트리밍한다. LLM 호출은 이 파일에만.

    is_refine=True + prior_proposal 제공 시 REFINE_PROMPT로 실제 변경 내용을 설명한다 (F6 AC3).
    schemas/CLAUDE.md: text 청크는 "LLM 토큰 단위 응답 (delta 누적은 FE가 처리)".
    """
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    from agent.prompts import REFINE_PROMPT, SYSTEM_PROMPT

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3, api_key=api_key)

    current_text = _format_slots(proposal.get("slots", []))

    if is_refine and prior_proposal is not None:
        previous_text = _format_slots(prior_proposal.get("slots", []))
        prompt = REFINE_PROMPT.format(
            user_feedback=user_input,
            previous_proposal=previous_text,
            updated_proposal=current_text,
        )
    else:
        prompt = (
            f"사용자 요청: {user_input}\n\n"
            f"이번 주 운동 스케줄:\n{current_text}\n\n"
            "위 스케줄을 따뜻하고 격려하는 톤으로 2~3문장으로 소개해 주세요. 한국어로."
        )

    async for chunk in llm.astream([
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=prompt),
    ]):
        yield chunk.content


def refine_node(state: dict) -> dict:
    """멀티턴 재조정 노드.

    사용자 피드백에서 요일을 파싱해 해당 날짜 슬롯만 교체한다.
    나머지 슬롯과 fatigue_timeline은 그대로 유지 (KPI #4).
    """
    user_input: str = state.get("user_input", "")
    user_intent = _parse_user_intent(user_input)
    proposal_dict = state.get("proposal")
    if not proposal_dict:
        return {}

    proposal = ScheduleProposal.model_validate(proposal_dict)
    target_weekday = _parse_target_weekday(user_input)

    # 요일을 파악하지 못하면 기존 제안 그대로 반환
    if target_weekday is None:
        return {"proposal": proposal.model_dump(mode="json")}

    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    target_date = week_start + datetime.timedelta(days=target_weekday)

    # target_date를 제외한 나머지 슬롯 (피로도 계산 + 최종 조합에 모두 사용)
    other_slots = [s for s in proposal.slots if s.start.date() != target_date]

    # 현재 슬롯 부위를 파악해 refine 선택에서 제외 → "바꿔줘" 요청이 실제로 다른 결과를 냄
    current_slot = next((s for s in proposal.slots if s.start.date() == target_date), None)
    excluded_muscles = frozenset(current_slot.target_muscles) if current_slot else frozenset()

    calendar: list[dict] = state.get("calendar_data", [])
    health: list[dict] = state.get("health_data", [])
    workouts: list[dict] = state.get("workouts_data", [])

    # DB 기록 피로도 + 이미 제안된 슬롯(target_date 이전)의 누적 피로도를 합산
    base_fatigue = _compute_muscle_fatigue(workouts)
    proposal_fatigue = _compute_proposal_fatigue(other_slots, target_date)
    fatigue = {
        m: min(5.0, base_fatigue.get(m, 0.0) + proposal_fatigue.get(m, 0.0))
        for m in _MUSCLES
    }
    condition = _assess_condition(health)

    busy = _busy_intervals(calendar, target_date)
    free_windows = _find_free_windows(busy, target_date)

    if not free_windows:
        alt_start = datetime.datetime(
            target_date.year, target_date.month, target_date.day, 7, 0
        )
        new_slot = WorkoutSlot(
            start=alt_start,
            end=alt_start + datetime.timedelta(minutes=10),
            type="홈트",
            target_muscles=["코어"],
            intensity=1,
            rationale="재조정 요청 + 빈 시간 없음 → 10분 대체 루틴",
        )
    else:
        window_start, window_end = free_windows[0]
        avail_min = int((window_end - window_start).total_seconds() / 60)
        duration_min = min(_DEFAULT_DURATION_MIN, avail_min)
        slot_end = window_start + datetime.timedelta(minutes=duration_min)
        workout_type, target_muscles, intensity, rationale = _select_workout(
            fatigue, condition, duration_min,
            excluded_muscles=excluded_muscles,
            user_intent=user_intent,
        )
        new_slot = WorkoutSlot(
            start=window_start,
            end=slot_end,
            type=workout_type,
            target_muscles=target_muscles,
            intensity=intensity,
            rationale=f"재조정: {rationale}",
        )

    new_slots = sorted(other_slots + [new_slot], key=lambda s: s.start)

    updated = ScheduleProposal(slots=new_slots, fatigue_timeline=proposal.fatigue_timeline)
    return {"proposal": updated.model_dump(mode="json")}

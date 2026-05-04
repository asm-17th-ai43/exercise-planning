"""LangGraph 노드 정의. 담당: C(이유준).

ReAct 패턴: 1) 일정 확인 → 2) 건강 확인 → 3) 운동 기록 확인 → 스케줄 도출.
외부 LLM 호출은 이 파일 안에 모은다(다른 모듈에서 직접 OpenAI 호출 금지).
"""
from __future__ import annotations

import datetime

from schemas.models import MuscleFatigueState, ScheduleProposal, WorkoutSlot

# ReAct 3단계 강제 순서 (시스템 프롬프트와 그래프 구조 양쪽으로 보장)
_REACT_STEPS = ["get_calendar", "get_health", "get_workouts"]


def _this_week_range() -> tuple[str, str]:
    today = datetime.date.today()
    start = today - datetime.timedelta(days=today.weekday())  # 이번 주 월요일
    end = start + datetime.timedelta(days=6)
    return start.isoformat(), end.isoformat()


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
    """수집한 데이터로 ScheduleProposal을 생성한다.

    5/5 stub: 더미 슬롯 1개 반환. 5/6에 실제 LLM 기반 도출로 교체.
    """
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    stub_slot = WorkoutSlot(
        start=datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 7, 0),
        end=datetime.datetime(tomorrow.year, tomorrow.month, tomorrow.day, 8, 0),
        type="유산소",
        target_muscles=["전신"],
        intensity=2,
        rationale="(stub) 데이터 수집 완료. 실제 제안은 5/6 이후.",
    )
    proposal = ScheduleProposal(slots=[stub_slot], fatigue_timeline=[])
    return {"proposal": proposal.model_dump(mode="json")}


def refine_node(state: dict) -> dict:
    """멀티턴 재조정 노드. 5/7 구현 예정."""
    raise NotImplementedError("5/7 구현 예정")

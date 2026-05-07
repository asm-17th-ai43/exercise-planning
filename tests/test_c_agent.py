"""C 슬라이스 (이유준) — Agent 스모크 테스트."""
import pytest

from agent.graph import run_agent, run_agent_stream
from agent.prompts import SYSTEM_PROMPT
from schemas.models import AgentResponse, ChatChunk


def test_system_prompt_has_react_steps():
    """시스템 프롬프트에 ReAct 3단계 키워드가 모두 포함되어야 한다."""
    assert "get_calendar" in SYSTEM_PROMPT
    assert "get_health" in SYSTEM_PROMPT
    assert "get_workouts" in SYSTEM_PROMPT


@pytest.mark.asyncio
async def test_run_agent_stream_yields_chunks():
    """`run_agent_stream`이 ChatChunk를 yield하는 async iterator여야 한다."""
    chunks = []
    async for chunk in run_agent_stream("테스트 입력", thread_id="test-thread"):
        assert isinstance(chunk, ChatChunk)
        chunks.append(chunk)

    assert len(chunks) > 0, "청크가 하나도 없음"
    types = [c.type for c in chunks]
    assert "done" in types, "done 청크가 없음"


@pytest.mark.asyncio
async def test_run_agent_stream_done_has_thread_id():
    """done 청크의 payload에 thread_id가 있어야 한다."""
    thread_id = "my-thread-123"
    async for chunk in run_agent_stream("입력", thread_id=thread_id):
        if chunk.type == "done":
            assert chunk.payload.get("thread_id") == thread_id
            break


@pytest.mark.asyncio
async def test_run_agent_stream_default_thread_id():
    """thread_id를 넘기지 않아도 done 청크에 thread_id가 있어야 한다."""
    async for chunk in run_agent_stream("입력"):
        if chunk.type == "done":
            assert chunk.payload.get("thread_id")
            break


# --- 5/5 합격 기준: 입력 → think → tool_call(stub) → done 흐름 ---

@pytest.mark.asyncio
async def test_react_three_tool_calls_emitted():
    """ReAct 3단계 tool_call 청크가 순서대로 나와야 한다."""
    tool_calls = []
    async for chunk in run_agent_stream("이번 주 운동 짜줘", thread_id="flow-test"):
        if chunk.type == "tool_call":
            tool_calls.append(chunk.payload["name"])

    assert tool_calls == ["get_calendar", "get_health", "get_workouts"], (
        f"예상 순서와 다름: {tool_calls}"
    )


@pytest.mark.asyncio
async def test_proposal_chunk_emitted():
    """스케줄 도출 후 proposal 청크가 나와야 한다."""
    async for chunk in run_agent_stream("이번 주 운동 짜줘", thread_id="proposal-test"):
        if chunk.type == "proposal":
            assert "slots" in chunk.payload, "slots 키 없음"
            return
    pytest.fail("proposal 청크가 emit되지 않았음")


@pytest.mark.asyncio
async def test_full_flow_order():
    """tool_call 3개 → proposal → done 순서로 emit되어야 한다."""
    sequence = []
    async for chunk in run_agent_stream("이번 주 운동 짜줘", thread_id="order-test"):
        sequence.append(chunk.type)

    assert sequence.count("tool_call") == 3, f"tool_call 3개 예상, 실제: {sequence}"
    assert sequence.index("proposal") > sequence.index("tool_call"), "proposal이 tool_call 전에 나옴"
    assert sequence[-1] == "done", "마지막 청크가 done이 아님"


def test_run_agent_returns_agent_response():
    """run_agent(비스트림)가 AgentResponse를 반환해야 한다."""
    response = run_agent("안녕", session_state={})
    assert isinstance(response, AgentResponse)


# --- 5/6 합격 기준: 의미 있는 ScheduleProposal 도출 ---

import datetime
from agent.nodes import (
    _compute_muscle_fatigue,
    _assess_condition,
    _find_free_windows,
    _busy_intervals,
    _select_workout,
    compose_schedule_node,
)
from schemas.models import ScheduleProposal, WorkoutSlot, MuscleFatigueState


def test_compute_muscle_fatigue_recent_workout():
    """최근 운동 부위의 피로도가 0보다 커야 한다."""
    today = datetime.date.today()
    workouts = [
        {"date": today.isoformat(), "muscles": ["가슴", "삼두"], "intensity": 4},
    ]
    fatigue = _compute_muscle_fatigue(workouts)
    assert fatigue["가슴"] > 0
    assert fatigue["삼두"] > 0
    assert fatigue["등"] == 0.0


def test_compute_muscle_fatigue_old_workout_ignored():
    """8일 이상 된 운동은 피로도에 반영되지 않아야 한다."""
    old_date = (datetime.date.today() - datetime.timedelta(days=8)).isoformat()
    workouts = [{"date": old_date, "muscles": ["등"], "intensity": 5}]
    fatigue = _compute_muscle_fatigue(workouts)
    assert fatigue["등"] == 0.0


def test_find_free_windows_all_day_busy():
    """하루 종일 busy이면 빈 창이 없어야 한다."""
    target = datetime.date(2026, 5, 6)
    busy = [
        (datetime.datetime(2026, 5, 6, 6, 0), datetime.datetime(2026, 5, 6, 22, 0))
    ]
    assert _find_free_windows(busy, target) == []


def test_find_free_windows_morning_free():
    """오전이 비어 있으면 빈 창이 반환되어야 한다."""
    target = datetime.date(2026, 5, 6)
    busy = [
        (datetime.datetime(2026, 5, 6, 9, 0), datetime.datetime(2026, 5, 6, 22, 0))
    ]
    windows = _find_free_windows(busy, target)
    assert len(windows) == 1
    assert windows[0][0].hour == 6


def test_select_workout_avoids_high_fatigue():
    """피로도 4 이상 부위는 선택되지 않아야 한다 (KPI #2)."""
    fatigue = {m: 0.0 for m in ["가슴", "등", "하체", "어깨", "코어", "이두", "삼두"]}
    fatigue["하체"] = 4.5
    fatigue["코어"] = 4.0
    condition = {"avg_sleep": 7.0, "avg_activity": 40, "fatigue_flag": False}

    _, target_muscles, _, _ = _select_workout(fatigue, condition, slot_min=60)
    assert "하체" not in target_muscles
    assert "코어" not in target_muscles


def test_compose_schedule_no_free_time_gives_alternative():
    """빈 시간이 없는 날은 10분 대체 루틴이 포함되어야 한다 (KPI #3)."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    monday = week_start

    # 월요일 전체를 꽉 채운 캘린더
    calendar = [{
        "start_at": datetime.datetime(monday.year, monday.month, monday.day, 6, 0).isoformat(),
        "end_at": datetime.datetime(monday.year, monday.month, monday.day, 22, 0).isoformat(),
        "is_busy": True,
    }]
    state = {"calendar_data": calendar, "health_data": [], "workouts_data": []}
    result = compose_schedule_node(state)

    proposal = ScheduleProposal.model_validate(result["proposal"])
    monday_slots = [s for s in proposal.slots if s.start.date() == monday]
    assert len(monday_slots) == 1
    assert monday_slots[0].intensity == 1
    duration = int((monday_slots[0].end - monday_slots[0].start).total_seconds() / 60)
    assert duration <= 10


def test_compose_schedule_proposal_has_all_muscles_in_fatigue():
    """fatigue_timeline의 각 항목이 7개 부위를 모두 가져야 한다 (KPI #5)."""
    state = {"calendar_data": [], "health_data": [], "workouts_data": []}
    result = compose_schedule_node(state)
    proposal = ScheduleProposal.model_validate(result["proposal"])

    assert len(proposal.fatigue_timeline) == 7
    for ft in proposal.fatigue_timeline:
        for muscle in ["가슴", "등", "하체", "어깨", "코어", "이두", "삼두"]:
            assert muscle in ft.fatigue, f"{ft.date}: {muscle} 누락"


def test_compose_schedule_no_conflict_with_busy():
    """추천 슬롯이 is_busy=True 일정과 겹치지 않아야 한다 (KPI #1)."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    monday = week_start

    calendar = [{
        "start_at": datetime.datetime(monday.year, monday.month, monday.day, 9, 0).isoformat(),
        "end_at": datetime.datetime(monday.year, monday.month, monday.day, 18, 0).isoformat(),
        "is_busy": True,
    }]
    state = {"calendar_data": calendar, "health_data": [], "workouts_data": []}
    result = compose_schedule_node(state)
    proposal = ScheduleProposal.model_validate(result["proposal"])

    busy_start = datetime.datetime(monday.year, monday.month, monday.day, 9, 0)
    busy_end = datetime.datetime(monday.year, monday.month, monday.day, 18, 0)
    for slot in proposal.slots:
        if slot.start.date() == monday:
            # 슬롯이 busy 구간과 겹치지 않아야 함
            no_overlap = slot.end <= busy_start or slot.start >= busy_end
            assert no_overlap, f"충돌 발생: {slot.start}~{slot.end}"


# --- 5/7 합격 기준: 멀티턴 재조정 ---

from agent.nodes import _parse_target_weekday, refine_node


def test_parse_target_weekday_full_name():
    """'화요일' 파싱 → 1."""
    assert _parse_target_weekday("화요일은 피곤할 것 같아") == 1


def test_parse_target_weekday_short():
    """'목' 파싱 → 3."""
    assert _parse_target_weekday("목 운동 바꿔줘") == 3


def test_parse_target_weekday_none():
    """요일 없으면 None."""
    assert _parse_target_weekday("운동 강도 낮춰줘") is None


def test_refine_node_replaces_only_target_day():
    """refine_node는 지정 요일 슬롯만 교체해야 한다 (KPI #4)."""
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())

    # 초기 proposal 생성
    initial_result = compose_schedule_node({"calendar_data": [], "health_data": [], "workouts_data": []})
    proposal = ScheduleProposal.model_validate(initial_result["proposal"])
    original_slots = {s.start.date(): s for s in proposal.slots}

    # 화요일(weekday=1) 재조정
    tuesday = week_start + datetime.timedelta(days=1)
    state = {
        "user_input": "화요일 운동 바꿔줘",
        "proposal": initial_result["proposal"],
        "calendar_data": [],
        "health_data": [],
        "workouts_data": [],
    }
    result = refine_node(state)
    refined = ScheduleProposal.model_validate(result["proposal"])
    refined_slots = {s.start.date(): s for s in refined.slots}

    assert len(refined.slots) == 7, "슬롯 수가 7개여야 함"
    for d, slot in original_slots.items():
        if d == tuesday:
            continue  # 화요일은 변경 허용
        assert refined_slots[d].start == slot.start, f"{d}: 변경되면 안 되는 슬롯이 변경됨"


def test_refine_node_unknown_day_returns_unchanged():
    """요일을 파악 못하면 기존 proposal 그대로 반환."""
    initial_result = compose_schedule_node({"calendar_data": [], "health_data": [], "workouts_data": []})
    state = {
        "user_input": "운동 강도 낮춰줘",
        "proposal": initial_result["proposal"],
        "calendar_data": [],
        "health_data": [],
        "workouts_data": [],
    }
    result = refine_node(state)
    assert result["proposal"] == initial_result["proposal"]


@pytest.mark.asyncio
async def test_multiturn_second_call_is_refine_mode():
    """같은 thread_id 두 번째 호출은 tool_call 없이 proposal만 emit해야 한다."""
    tid = "multiturn-refine-mode-test"
    # 1차 호출: 초기 스케줄
    async for _ in run_agent_stream("이번 주 운동 짜줘", thread_id=tid):
        pass

    # 2차 호출: 재조정 (tool_call 없어야 함)
    chunks = []
    async for chunk in run_agent_stream("화요일은 피곤할 것 같아서 쉬고 싶어", thread_id=tid):
        chunks.append(chunk)

    types = [c.type for c in chunks]
    assert "tool_call" not in types, f"재조정에서 tool_call이 나옴: {types}"
    assert "proposal" in types, "재조정에서 proposal이 없음"
    assert types[-1] == "done"


@pytest.mark.asyncio
async def test_multiturn_second_proposal_has_seven_slots():
    """재조정 후 proposal도 7개 슬롯을 가져야 한다."""
    tid = "multiturn-seven-slots-test"
    async for _ in run_agent_stream("이번 주 운동 짜줘", thread_id=tid):
        pass

    second_proposal = None
    async for chunk in run_agent_stream("화요일 운동 바꿔줘", thread_id=tid):
        if chunk.type == "proposal":
            second_proposal = chunk.payload

    assert second_proposal is not None
    assert len(second_proposal["slots"]) == 7

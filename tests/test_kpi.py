"""KPI 시나리오 테스트 — D(박영준) 담당: KPI 1·3.

LLM·Supabase 불필요 — compose_schedule_node 직접 호출 (순수 Python 결정론적 로직).
pytest -m kpi 로만 실행 (통합·데모 시점).
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from agent.nodes import compose_schedule_node
from schemas.models import ScheduleProposal

SCENARIOS_DIR = Path(__file__).parent.parent / "data" / "scenarios"
_SCENARIO_WEEK_START = date(2026, 5, 4)  # 시나리오 JSON 기준 월요일


def _load_scenario(name: str) -> dict:
    return json.loads((SCENARIOS_DIR / name).read_text())


def _shift_to_current_week(scenario: dict) -> dict:
    """시나리오 날짜를 현재 주 월요일 기준으로 조정."""
    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    delta_days = (current_week_start - _SCENARIO_WEEK_START).days

    sc = json.loads(json.dumps(scenario))  # deep copy

    def shift_dt(s: str) -> str:
        return (datetime.fromisoformat(s) + timedelta(days=delta_days)).isoformat()

    def shift_d(s: str) -> str:
        return (date.fromisoformat(s) + timedelta(days=delta_days)).isoformat()

    for ev in sc.get("calendar", []):
        ev["start_at"] = shift_dt(ev["start_at"])
        ev["end_at"] = shift_dt(ev["end_at"])
    for h in sc.get("health", []):
        h["date"] = shift_d(h["date"])
    for w in sc.get("workouts", []):
        w["date"] = shift_d(w["date"])

    return sc


def _has_conflict(proposal: ScheduleProposal, calendar: list[dict]) -> list[str]:
    """busy 일정과 겹치는 슬롯 목록 반환. 빈 리스트면 충돌 없음."""
    conflicts = []
    for slot in proposal.slots:
        for ev in calendar:
            if not ev.get("is_busy", True):
                continue
            ev_start = datetime.fromisoformat(ev["start_at"])
            ev_end = datetime.fromisoformat(ev["end_at"])
            if ev_start.date() != slot.start.date():
                continue
            if slot.start < ev_end and slot.end > ev_start:
                conflicts.append(
                    f"{slot.start.date()} {slot.start.strftime('%H:%M')}~"
                    f"{slot.end.strftime('%H:%M')} ↔ {ev_start.strftime('%H:%M')}~{ev_end.strftime('%H:%M')}"
                )
    return conflicts


@pytest.mark.kpi
def test_kpi1_no_schedule_conflict():
    """KPI 1: 10회 생성 시 is_busy 일정과 충돌 0회.

    결정론적 코드이므로 10회 반복은 동일 결과를 보장.
    03_consecutive_muscle 시나리오: 평일 09:00~18:00 busy → 자유 시간 06:00~09:00.
    """
    sc = _shift_to_current_week(_load_scenario("03_consecutive_muscle.json"))
    state = {
        "calendar_data": sc["calendar"],
        "health_data": sc["health"],
        "workouts_data": sc["workouts"],
    }

    for i in range(10):
        result = compose_schedule_node(state)
        proposal = ScheduleProposal.model_validate(result["proposal"])
        conflicts = _has_conflict(proposal, sc["calendar"])
        assert not conflicts, f"[{i+1}/10] 충돌 발생:\n" + "\n".join(conflicts)


@pytest.mark.kpi
def test_kpi3_full_week_short_routine():
    """KPI 3: 빈 시간 없는 주에 10분 대체 루틴 제안.

    01_full_week 시나리오: 매일 06:00~22:00 busy → 자유 시간 0.
    모든 슬롯이 10분 이하 대체 루틴이어야 함.
    """
    sc = _shift_to_current_week(_load_scenario("01_full_week.json"))
    state = {
        "calendar_data": sc["calendar"],
        "health_data": sc["health"],
        "workouts_data": sc["workouts"],
    }

    result = compose_schedule_node(state)
    proposal = ScheduleProposal.model_validate(result["proposal"])

    assert len(proposal.slots) == 7, "7일치 슬롯이 모두 있어야 함"
    for slot in proposal.slots:
        duration = int((slot.end - slot.start).total_seconds() / 60)
        assert duration <= 10, (
            f"{slot.start.date()}: {duration}분 슬롯 — 빈 시간 없을 때 10분 이하여야 함"
        )
        assert slot.intensity <= 1, (
            f"{slot.start.date()}: 강도 {slot.intensity} — 대체 루틴은 강도 1 이하여야 함"
        )

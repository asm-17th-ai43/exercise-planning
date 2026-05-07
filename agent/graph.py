"""LangGraph StateGraph 골격 + 진입점. 담당: C(이유준)."""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import TypedDict

from langgraph.graph import END, StateGraph

from memory import checkpointer
from schemas.models import AgentResponse, ChatChunk
from agent.nodes import call_tool_node, compose_schedule_node, refine_node, think_node


class AgentState(TypedDict):
    user_input: str
    thread_id: str | None
    mode: str                     # "schedule" | "refine"
    tools_called: list[str]       # 이미 호출된 Tool 이름 목록
    next_action: str              # think_node가 결정한 다음 동작
    calendar_data: list[dict]
    health_data: list[dict]
    workouts_data: list[dict]
    proposal: dict | None


def _route_after_think(state: AgentState) -> str:
    """think 노드 이후 분기: Tool 호출 / 스케줄 도출 / 재조정."""
    action = state["next_action"]
    if action == "compose":
        return "compose_schedule"
    if action == "refine":
        return "refine"
    return "call_tool"


# --- 그래프 조립 ---
_builder = StateGraph(AgentState)
_builder.add_node("think", think_node)
_builder.add_node("call_tool", call_tool_node)
_builder.add_node("compose_schedule", compose_schedule_node)
_builder.add_node("refine", refine_node)

_builder.set_entry_point("think")
_builder.add_conditional_edges(
    "think",
    _route_after_think,
    {"call_tool": "call_tool", "compose_schedule": "compose_schedule", "refine": "refine"},
)
_builder.add_edge("call_tool", "think")  # Tool 호출 후 다시 think
_builder.add_edge("compose_schedule", END)
_builder.add_edge("refine", END)

graph = _builder.compile(checkpointer=checkpointer)


# --- 진입점 ---

def run_agent(user_input: str, session_state: dict) -> AgentResponse:
    """비스트림 진입점 — 테스트·단순 호출용."""
    config = {"configurable": {"thread_id": "test-sync"}}
    initial: AgentState = {
        "user_input": user_input,
        "thread_id": None,
        "mode": "schedule",
        "tools_called": [],
        "next_action": "",
        "calendar_data": [],
        "health_data": [],
        "workouts_data": [],
        "proposal": None,
    }
    result = graph.invoke(initial, config)
    return AgentResponse(
        message="(stub) 스케줄 도출 완료",
        proposal=None,
        needs_approval=True,
    )


def _has_prior_proposal(config: dict) -> bool:
    """체크포인터에 해당 thread의 이전 proposal이 있는지 확인."""
    prev = checkpointer.get_tuple(config)
    if not prev:
        return False
    return bool(prev.checkpoint.get("channel_values", {}).get("proposal"))


async def run_agent_stream(
    user_input: str,
    thread_id: str | None = None,
) -> AsyncIterator[ChatChunk]:
    """SSE 스트림 진입점 — backend/api/chat.py가 호출.

    같은 thread_id로 이전 proposal이 있으면 refine 모드로 동작.
    ChatChunk(type ∈ text/tool_call/proposal/done/error)를 순차 yield.
    chunk별 payload 스키마는 schemas/CLAUDE.md 참고.
    """
    tid = thread_id or "default-thread"
    config = {"configurable": {"thread_id": tid}}

    if _has_prior_proposal(config):
        # 재조정: user_input·mode만 업데이트, 나머지(calendar/health/workouts/proposal)는 체크포인터에서 복원
        initial: dict = {
            "user_input": user_input,
            "mode": "refine",
            "tools_called": [],
            "next_action": "",
        }
    else:
        initial = {
            "user_input": user_input,
            "thread_id": tid,
            "mode": "schedule",
            "tools_called": [],
            "next_action": "",
            "calendar_data": [],
            "health_data": [],
            "workouts_data": [],
            "proposal": None,
        }

    try:
        async for update in graph.astream(initial, config, stream_mode="updates"):
            for node_name, node_update in update.items():
                if node_name == "think":
                    action = node_update.get("next_action", "")
                    if action and action not in ("compose", "refine"):
                        yield ChatChunk(
                            type="tool_call",
                            payload={"name": action, "args": {}},
                        )
                elif node_name in ("compose_schedule", "refine"):
                    if proposal := node_update.get("proposal"):
                        yield ChatChunk(type="proposal", payload=proposal)
    except Exception as exc:
        yield ChatChunk(type="error", payload={"message": str(exc)})
        return

    yield ChatChunk(type="done", payload={"thread_id": tid})

"""LangGraph StateGraph 골격 + 진입점.

담당: C(이유준).
5/8 통합일까지는 stub 응답을 돌려도 됨.
"""
from collections.abc import AsyncIterator

from schemas.models import AgentResponse, ChatChunk


def run_agent(user_input: str, session_state: dict) -> AgentResponse:
    """비스트림 진입점 — 테스트·단순 호출용.

    구현 전엔 더미 응답을 돌려 UI/타 슬라이스가 병렬로 작업할 수 있게 한다.
    """
    return AgentResponse(
        message=(
            "안녕하세요, 박장우님의 퍼스널 트레이너입니다. "
            "(stub) 입력: " + user_input
        ),
        proposal=None,
        needs_approval=False,
    )


async def run_agent_stream(
    user_input: str,
    thread_id: str | None = None,
) -> AsyncIterator[ChatChunk]:
    """SSE 스트림 진입점 — backend/api/chat.py가 호출.

    ChatChunk(type ∈ text/tool_call/proposal/done/error)를 순차 yield.
    chunk별 payload 스키마는 schemas/CLAUDE.md 참고.
    """
    yield ChatChunk(type="text", payload={"delta": "(stub) "})
    yield ChatChunk(type="text", payload={"delta": user_input})
    yield ChatChunk(type="done", payload={"thread_id": thread_id or "stub-thread"})

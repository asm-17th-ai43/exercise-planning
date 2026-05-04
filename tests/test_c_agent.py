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

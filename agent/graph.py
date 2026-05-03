"""LangGraph StateGraph 골격 + Streamlit 진입점.

담당: #3 (그래프 구조), #4 (노드 채움).
5/8 통합일까지는 stub 응답을 돌려도 됨.
"""
from schemas import AgentResponse


def run_agent(user_input: str, session_state: dict) -> AgentResponse:
    """Streamlit이 호출하는 진입점.

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

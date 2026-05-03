"""LangGraph 노드 정의. 담당: #4.

ReAct 패턴: 1) 일정 확인 → 2) 건강 확인 → 3) 운동 기록 확인 → 스케줄 도출.
외부 LLM 호출은 이 파일 안에 모은다(다른 모듈에서 직접 OpenAI 호출 금지).
"""


def think_node(state: dict) -> dict:
    raise NotImplementedError("담당: #4")


def call_tool_node(state: dict) -> dict:
    raise NotImplementedError("담당: #4")


def compose_schedule_node(state: dict) -> dict:
    raise NotImplementedError("담당: #4")

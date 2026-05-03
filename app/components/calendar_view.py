"""사용자 일정 카드 컴포넌트. 담당: #1."""
import streamlit as st

from schemas import CalendarEvent


def render(events: list[CalendarEvent]) -> None:
    """이번 주 일정을 카드/리스트로 렌더링. 비어 있으면 안내 메시지."""
    raise NotImplementedError("담당: #1 캘린더 슬라이스")

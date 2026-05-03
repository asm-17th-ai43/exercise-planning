"""건강(수면·활동량) 카드 컴포넌트. 담당: #2."""
import streamlit as st

from schemas import HealthSnapshot


def render(snapshots: list[HealthSnapshot]) -> None:
    """최근 며칠치 수면·활동량을 메트릭 카드로 렌더링."""
    raise NotImplementedError("담당: #2 건강 슬라이스")

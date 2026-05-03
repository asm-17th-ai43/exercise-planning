"""근육 부위별 피로도 이미지 생성. 담당: #5.

운동 → 부위 매핑 + 누적 피로도 → 부위별 색상 오버레이.
1차: Pillow + 사전 제작 SVG/PNG 합성. 2차(시간 남으면): 이미지 모델 호출.
"""
from schemas import MuscleFatigueState


def render_fatigue(state: MuscleFatigueState) -> bytes:
    """주어진 부위별 피로도(0~5)를 시각화한 PNG 바이트를 반환."""
    raise NotImplementedError("담당: #5 시각화 슬라이스")

"""Streamlit 진입점. 담당: #5 (#1, #2 컴포넌트는 각 담당이 PR로 추가)."""
import streamlit as st

from agent.graph import run_agent

st.set_page_config(page_title="맞춤형 운동 스케줄링 에이전트", layout="wide")

st.title("맞춤형 운동 스케줄링 에이전트")
st.caption("바쁜 일정과 컨디션에 맞춰, 이번 주 운동을 알아서 계획해드립니다.")

if "messages" not in st.session_state:
    st.session_state.messages = []

left, right = st.columns([2, 1])

with left:
    st.subheader("대화")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("예) 앞으로 7일 운동 일정 추천해줘"):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        response = run_agent(user_input, dict(st.session_state))
        st.session_state.messages.append({"role": "assistant", "content": response.message})
        with st.chat_message("assistant"):
            st.markdown(response.message)

        if response.proposal:
            st.subheader("제안된 스케줄")
            st.json(response.proposal.model_dump(mode="json"))

        if response.needs_approval:
            st.button("캘린더에 등록", type="primary")

with right:
    st.subheader("내 일정")
    st.info("#1 캘린더 슬라이스에서 calendar_view를 여기에 import해 렌더링.")

    st.subheader("최근 컨디션")
    st.info("#2 건강 슬라이스에서 health_card를 여기에 import해 렌더링.")

    st.subheader("근육 피로도")
    st.info("#5 시각화 슬라이스에서 render_fatigue 결과를 표시.")

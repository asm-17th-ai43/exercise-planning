# app/ — Streamlit UI

> **담당**: #5 `main.py` + 채팅·승인 플로우 · #1 `components/calendar_view.py` · #2 `components/health_card.py`

## 구조 분담

- **`main.py`** (#5) — 페이지 레이아웃, 채팅 입력, `run_agent` 호출, 결과 렌더링, 캘린더 등록 승인 버튼
- **`components/`** — 슬라이스별 UI 위젯. **함수 하나만 export** (`render(data) -> None`)
  - `calendar_view.py` — #1 일정 카드/타임라인
  - `health_card.py` — #2 수면·활동량 메트릭
  - 피로도 이미지는 `visuals.muscle_map.render_fatigue` 결과를 `main.py`에서 직접 표시

## Agent 호출 패턴

```python
from agent.graph import run_agent

response = run_agent(user_input, dict(st.session_state))
st.session_state.messages.append({"role": "assistant", "content": response.message})
if response.proposal:
    st.json(response.proposal.model_dump(mode="json"))
if response.needs_approval:
    st.button("캘린더에 등록", type="primary")
```

`session_state`는 dict로 변환해서 넘기기 (Streamlit 객체를 그대로 노출 X).

## 멀티턴

`st.session_state.messages`에 `{role, content}` dict 누적. LangGraph 메모리는 별도이므로 thread_id를 session_state에 저장:

```python
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
```

## UI 룰

- 사용자에게 보이는 모든 문자열은 **한국어**
- `st.chat_message("user" | "assistant")` 사용
- 로딩 중은 `with st.spinner("스케줄 짜는 중..."):` 로 감싸기
- 에러는 `st.error()`로 표시하고 stack trace는 숨기기 (개발 중엔 `st.exception()`)

## 실행

```bash
streamlit run app/main.py
```

UI 변경 후엔 **반드시 브라우저로 동작 확인**한 뒤 PR.

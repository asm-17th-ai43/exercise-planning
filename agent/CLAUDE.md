# agent/ — LangGraph Agent

> **담당**: #3 `graph.py` (Tech Lead 후보) · #4 `nodes.py`, `prompts.py`

## 파일 분담

- **`graph.py`** — `StateGraph` 정의, 노드 연결, 컴파일, **Streamlit 진입점 `run_agent`**
- **`nodes.py`** — 개별 노드 함수 (think / call_tool / compose_schedule / refine), **외부 LLM 호출은 여기에만**
- **`prompts.py`** — 시스템 프롬프트 (ReAct 강제), 페르소나 톤, 멀티턴 재조정 템플릿

다른 모듈에서 OpenAI/LLM을 직접 호출하지 말 것. 전부 `nodes.py`로 라우팅.

## ReAct 강제 패턴

시스템 프롬프트로 다음 3단계를 **반드시 순서대로** 거치게 강제:

1. `get_calendar` — 사용자 일정 확인
2. `get_health` — 최근 수면·활동량 확인
3. `get_workouts` — 최근 운동 기록 확인

위 단계 결과만 근거로 `ScheduleProposal`을 도출 (환각 방지).

## 그래프 골격 (예시)

```
[user_input]
    ↓
[think] ─→ tool 호출 필요? ─yes→ [call_tool] → [think]
    ↓ no
[compose_schedule] → AgentResponse
```

수정 요청 시:
```
[user_input(피드백)] → [refine] → 변경된 ScheduleProposal
```

## 메모리

LangGraph 체크포인터는 `memory/` 모듈에서 정의. `graph.py`에서 컴파일할 때 `checkpointer=...` 인자로 주입. 멀티턴 동안 동일 `thread_id`로 호출.

## stub → 실구현 순서

- 5/4: `run_agent`가 `AgentResponse`를 더미로 반환 (이미 구현됨)
- 5/5: stub Tool 호출로 그래프 1회 실행
- 5/6: 실제 LLM 호출, 실제 Tool 연결, `ScheduleProposal` 도출
- 5/7: 멀티턴 메모리, refine 노드 추가
- 5/8: 통합 테스트

## 작업 시 주의

- 한 노드 = 한 책임 (조건 분기는 conditional edge로 빼기)
- 노드 함수의 입력/출력 dict 키는 명확히 명명 (`messages`, `tool_calls`, `proposal` 등)
- LLM 호출은 `langchain_openai.ChatOpenAI` 사용, 모델은 `gpt-4o`
- API 키는 `os.getenv("OPENAI_API_KEY")`로 읽고, 없으면 명확히 에러

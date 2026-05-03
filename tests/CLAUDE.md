# tests/ — 스모크/단위 테스트

> **담당**: 전원이 자기 슬라이스 테스트 추가

## 실행

```bash
pytest                       # 전체
pytest tests/test_smoke.py   # 스모크만
pytest -k calendar           # 키워드 매칭
```

5/4 EOD부터 매 PR이 `pytest` 통과해야 머지.

## 작성 규칙

- 파일명: `test_<slice>.py` (`test_calendar.py`, `test_agent_graph.py` 등)
- 한 테스트 = 한 가지 검증. assert 메시지 한국어 OK.
- 외부 LLM 호출이 필요한 테스트는 `@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), ...)` 로 보호
- 가짜 데이터는 `tests/fixtures/`에 두고 fixture 함수로 로드

## 슬라이스별 최소 테스트 (5/5 EOD까지 1개씩)

- #1: `get_calendar`가 빈 범위에 빈 리스트를 돌려준다
- #2: `get_health`가 1주치 데이터를 모두 파싱한다
- #3: `get_workouts`가 부위 키 1종 이상 포함한다 + 그래프가 컴파일된다
- #4: 시스템 프롬프트에 ReAct 3단계 키워드가 들어 있다
- #5: `render_fatigue`가 0이 아닌 PNG 바이트를 반환한다 + Streamlit 컴포넌트가 import된다

## KPI 시나리오 테스트 (5/9까지)

`tests/test_kpi.py`에 시나리오 5개 (CLAUDE.md 9번 참조). LLM 호출 포함되므로 `@pytest.mark.kpi` 마커로 묶어 평소엔 스킵, 통합 시점에만 실행.

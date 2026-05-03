# 43조 — 맞춤형 운동 스케줄링 에이전트

> 5인 팀 공유 컨텍스트. 이 파일 수정은 데일리 싱크 합의 후 PR로만.
> **각 디렉토리에 자체 `CLAUDE.md`가 있음** — 슬라이스별 디테일은 거기에서 본다.

**한 줄 정의**: 캘린더·건강·운동기록을 종합해 이번 주 맞춤 운동 스케줄을 자동 생성하는 LangGraph Agent + Streamlit UI. 상세 기획은 `프로젝트 기획서 양식_43조_맞춤형 운동 스케줄링 에이전트.md` 참조.

## 1. 팀 & 담당 슬라이스 (B안 — 균등 분배)

| # | 슬라이스 | 담당자 | 디렉토리 |
|---|---|---|---|
| 1 | 캘린더 | _____ | `data/`, `tools/`, `app/components/calendar_view.py` |
| 2 | 건강 | _____ | `data/`, `tools/`, `app/components/health_card.py` |
| 3 | 운동기록 + 그래프 *(Tech Lead 후보)* | _____ | `data/`, `tools/`, `agent/graph.py` |
| 4 | 추론·프롬프트·메모리 *(Tech Lead 후보)* | _____ | `agent/nodes.py`, `agent/prompts.py`, `memory/` |
| 5 | 시각화·UX | _____ | `visuals/`, `app/main.py` |

**Tech Lead**(#3 또는 #4)는 매일 저녁 main 동작 확인 + 통합 책임.
**팀원**: 노준영 · 박영준 · 박장우 · 신승민 · 이유준 (5/4 킥오프에서 매칭)

## 2. 기술 스택

Python 3.11+ / OpenAI GPT-4o / LangGraph(+LangChain) / Streamlit / Pydantic v2 / Pillow. 데이터는 로컬 JSON만(실제 캘린더·헬스 API 미사용). 메모리는 LangGraph 체크포인터(in-memory→필요 시 SQLite). 의존성은 `requirements.txt` 고정, 추가 시 데일리 싱크 공지.

## 3. 레포 구조

```
AI_TECH_EDU/
├── app/         # Streamlit UI         → app/CLAUDE.md
├── agent/       # LangGraph Agent      → agent/CLAUDE.md
├── tools/       # 데이터 조회 Tool     → tools/CLAUDE.md
├── data/        # 가상 JSON            → data/CLAUDE.md
├── memory/      # 체크포인터           → memory/CLAUDE.md
├── visuals/     # 피로도 이미지        → visuals/CLAUDE.md
├── schemas/     # 공통 데이터 모델     → schemas/CLAUDE.md
├── tests/       # 스모크/단위 테스트   → tests/CLAUDE.md
└── 킥오프_5월4일.md  개발계획_*.md  requirements.txt  .env.example
```

작업 시작 전 자기 슬라이스 디렉토리의 `CLAUDE.md`를 먼저 읽기.

## 4. 인터페이스 진입점 (자세한 모델은 `schemas/CLAUDE.md`)

```python
# tools/data_tools.py
get_calendar(start, end) -> list[CalendarEvent]
get_health(start, end)   -> list[HealthSnapshot]
get_workouts(start, end) -> list[WorkoutRecord]

# agent/graph.py
run_agent(user_input: str, session_state: dict) -> AgentResponse

# visuals/muscle_map.py
render_fatigue(state: MuscleFatigueState) -> bytes  # PNG
```

위 시그니처는 **5/4 킥오프에서 락**. 변경 절차는 `schemas/CLAUDE.md` 참고.

## 5. 협업 규칙

- **Git**: `main` 보호, 브랜치 `feat/<slice>-<짧은설명>`, PR은 함수 단위로 작게, 리뷰어 1명 이상 승인 후 머지(셀프 머지 금지). 같은 파일(`tools/data_tools.py`, `app/main.py`)을 여럿이 만질 땐 싱크에서 머지 순서 정함.
- **Mock-first**: 데이터/타 슬라이스 함수가 없어도 `schemas/` 더미와 `NotImplementedError` stub으로 작업 시작. 실제 LLM 호출은 5/8 통합 전까지 stub 가능.
- **데일리 15분 싱크**: 어제/오늘/막힌 것. 인터페이스 변경 논의는 이 자리에서만.
- **시크릿**: `.env` 절대 커밋 금지(`.gitignore` 등록), 새 변수는 `.env.example`에 키만 추가.

## 6. 코딩 컨벤션

타입 힌트 필수. UI/챗 응답은 한국어, 코드·주석·식별자는 영어. 주석은 *왜*가 비자명할 때만. LangGraph 노드는 한 가지 일만. **외부 LLM 호출은 `agent/nodes.py` 한 곳에 모음**(다른 모듈 직접 호출 금지).

## 7. 환경 셋업

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # OPENAI_API_KEY 채우기
streamlit run app/main.py
pytest
```

## 8. 일정 (2026-05-04 ~ 05-10, 코드 동결)

| 날짜          | 마일스톤                                       |
| ----------- | ------------------------------------------ |
| 5/4 (월)     | 인터페이스 락, 레포 스캐폴딩, LangGraph 튜토리얼 1시간 페어 학습 |
| 5/5 (화)     | 각 슬라이스 더미 입력 단독 실행 가능                      |
| 5/6 (수)     | 핵심 로직 (1주치 데이터, Tool 연결, 스케줄 도출)           |
| 5/7 (목)     | 멀티턴 메모리, 재조정 흐름                            |
| **5/8 (금)** | **★ 1차 통합 — end-to-end 1회 성공**             |
| 5/9 (토)     | 통합 테스트, KPI 시나리오 5개, 엣지 케이스                |
| 5/10 (일)    | **코드 동결**, 데모 시나리오 무사고 시연, 태그 `v1.0-demo`  |

발표일: **2026-05-15(금)**. 5/11~14는 발표 자료·리허설.

## 9. KPI 시나리오 (5/9 통과 목표)

1. 일정 충돌률 1% 미만 (10회 생성 시 충돌 0회)
2. 피로도 "높음" 부위에 해당 부위 운동 추천 0회
3. 빈 시간 없는 주에 10분 대체 루틴(홈트·계단) 제안
4. 멀티턴 재조정 ("화요일은 피곤할 것 같아") → 해당 일자만 변경
5. 추천 부위와 피로도 이미지 색상 변화 일치

## 10. 절대 하지 말 것

- 실제 Google Calendar / Apple Health API 연동 (MVP 범위 외)
- `.env`·API 키 커밋, `main` 직접 push, 셀프 머지
- `schemas/models.py`·Tool 시그니처를 단독 결정으로 변경
- 다른 슬라이스 디렉토리를 합의 없이 리팩터링
- 사용자에게 보여줄 메시지를 영어로 작성

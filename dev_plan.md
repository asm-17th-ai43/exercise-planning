# 43조 개발 계획 — B안: 스택 무관 5명 균등 분배 (수직 슬라이스)

> **대상**: 노준영, 박영준, 박장우, 신승민, 이유준
> **개발 기간**: 2026-05-04(월) ~ 2026-05-10(일) (7일, 코드 동결)
> **발표일**: 2026-05-15(금)
> **MVP**: LangGraph 기반 운동 스케줄링 Agent + Streamlit UI + 근육 피로도 이미지

---

## 1. 분배 개요

각자 **수직 슬라이스(Vertical Slice) 1개**를 들고 가서 자기 슬라이스의 데이터·로직·UI를 끝까지 책임진다. 백/프론트 비대칭 없이 5명이 풀스택을 균등하게 경험.

| # | 슬라이스 | 책임 범위 | 주요 산출물 |
|---|---|---|---|
| 1 | **데이터 입력 슬라이스 (캘린더)** | 캘린더 가상 데이터 + 조회 Tool + Streamlit "내 일정" 뷰 | `data/calendar.json`, `tools/data_tools.py::get_calendar`, Streamlit 일정 컴포넌트 |
| 2 | **건강 슬라이스** | 건강(수면·활동량) 데이터 + 조회 Tool + 건강 요약 카드 UI | `data/health.json`, `tools/data_tools.py::get_health`, Streamlit 건강 카드 |
| 3 | **운동 기록 슬라이스 + Agent 그래프 골격** | 운동기록 데이터 + 조회 Tool + LangGraph StateGraph 골격(노드 연결) | `data/workouts.json`, `tools/data_tools.py::get_workouts`, `agent/graph.py` |
| 4 | **추론·프롬프트·메모리 슬라이스** | 시스템 프롬프트, ReAct 노드, 멀티턴 메모리, 스케줄 도출 로직 | `agent/prompts.py`, `agent/nodes.py`, `memory/` |
| 5 | **시각화·UX 슬라이스** | 근육 피로도 이미지 생성 + Streamlit 채팅창/승인 플로우 | `visuals/muscle_map.py`, `app/main.py` 채팅·승인 UI |

### 인접 협업 매트릭스
- #1·#2·#3은 데이터 형식이 비슷 → 5/4 킥오프에서 함께 스키마 합의
- #3은 그래프 골격을, #4는 그 위 노드를 채움 → 가장 긴밀한 페어
- #5는 #4의 `MuscleFatigueState`를 입력으로 받음
- **Tech Lead**: #3 또는 #4 담당 중 1명이 겸임 (그래프와 추론을 모두 보는 위치)

### 장점 / 리스크
- **장점**: 학습 효과 균등(전원이 LangGraph + Streamlit 둘 다 만져봄). 한 명 결근해도 다른 슬라이스는 계속 돈다.
- **리스크**: Streamlit·LangGraph 둘 다 처음 만지는 팀원에게 부담 → **5/4 킥오프에서 1시간 페어 학습 권장** (LangGraph 튜토리얼 1개를 다 같이 따라하기).

---

## 2. 통합 전략

핵심 원칙: **인터페이스 먼저 락 → 모두 Mock으로 병렬 → 후반 2일 통합**.

### 2-1. 레포 구조
```
exercise-agent/
├── app/                    # Streamlit 진입점 (담당: #5, 일정·건강 컴포넌트는 #1·#2가 PR)
│   └── main.py
├── agent/                  # LangGraph
│   ├── graph.py            # 담당: #3
│   ├── nodes.py            # 담당: #4
│   └── prompts.py          # 담당: #4
├── tools/                  # LangGraph Tool
│   └── data_tools.py       # 담당: #1·#2·#3 (각자 자기 함수 추가)
├── data/
│   ├── calendar.json       # 담당: #1
│   ├── health.json         # 담당: #2
│   └── workouts.json       # 담당: #3
├── memory/                 # 담당: #4
├── visuals/                # 담당: #5
│   └── muscle_map.py
├── schemas/                # 공통 데이터 모델 (전원이 import)
│   └── models.py
├── tests/
└── requirements.txt
```

### 2-2. 인터페이스 락 (5/4 킥오프 첫 1시간)
**`schemas/models.py`에 Pydantic 모델로 한 번만 정의**. 그 후엔 변경 시 전원 동의.

- **입력 모델**: `CalendarEvent`, `HealthSnapshot`, `WorkoutRecord`
- **Agent 산출 모델**: `ScheduleProposal`, `WorkoutSlot`, `MuscleFatigueState`, `AgentResponse`
- **Tool 시그니처**:
  ```python
  def get_calendar(start: date, end: date) -> list[CalendarEvent]: ...
  def get_health(start: date, end: date) -> list[HealthSnapshot]: ...
  def get_workouts(start: date, end: date) -> list[WorkoutRecord]: ...
  ```
- **Streamlit ↔ Agent 진입점**:
  ```python
  def run_agent(user_input: str, session_state: dict) -> AgentResponse: ...
  ```
- **이미지 진입점**:
  ```python
  def render_fatigue(state: MuscleFatigueState) -> bytes: ...
  ```

### 2-3. Mock-first 병렬화
- 데이터 슬라이스(#1·#2·#3)는 가짜 데이터부터 만들고, 다른 슬라이스는 그 더미를 import해서 시작.
- Agent 슬라이스(#3·#4)는 Tool stub만으로 그래프 골격을 먼저 짠다.
- UI 슬라이스(#5)는 `AgentResponse` 더미로 화면부터 만든다.

### 2-4. 협업 메커니즘
- **Git**: `main` 보호, 각자 `feat/<slice>` 브랜치 → PR → 리뷰 1명 이상 → 머지.
  - **주의**: B안에선 `tools/data_tools.py`와 `app/main.py`를 여러 명이 만진다. **함수 단위로 PR을 쪼개고**, 같은 파일 PR이 겹치면 즉시 싱크에서 머지 순서를 정한다.
- **Tech Lead**: #3 또는 #4 담당이 겸임. 매일 main이 깨졌는지 확인.
- **데일리 15분 싱크**: 어제 한 것 / 오늘 할 것 / 막힌 것. **인터페이스·공유 파일 변경은 이 자리에서만**.
- **공유 채널**: 카톡/디스코드 + GitHub PR 리뷰.
- **시크릿 관리**: OpenAI API 키는 `.env`, `.env.example`만 커밋.
- **페어 학습 (5/4 첫날)**: LangGraph 공식 튜토리얼 1개를 1시간 다 같이 따라하기.

---

## 3. 일정 (5/4 ~ 5/10)

| 날짜 | 마일스톤 | 전원 공통 | #1 캘린더 슬라이스 | #2 건강 슬라이스 | #3 운동기록+그래프 | #4 추론·프롬프트·메모리 | #5 시각화·UX |
|---|---|---|---|---|---|---|---|
| **5/4 (월)** | 인터페이스 락 + 학습 | 킥오프, `schemas/models.py` 합의·머지, 레포 스캐폴딩, LangGraph 튜토리얼 1시간 | `calendar.json` 더미 5건 | `health.json` 더미 5건 | `workouts.json` 더미 5건, `StateGraph` 골격 | 시스템 프롬프트 초안 | Streamlit 빈 페이지, 채팅 컴포넌트 골격 |
| **5/5 (화)** | 모듈 단독 실행 | 단위 테스트 1개씩 | `get_calendar` Tool, 일정 카드 컴포넌트 | `get_health` Tool, 건강 카드 컴포넌트 | `get_workouts` Tool, stub Tool로 그래프 1회 실행 | ReAct 3단계 강제 프롬프트, stub 노드 | `render_fatigue` 더미 입력으로 PNG 출력, 더미 `AgentResponse` 렌더 |
| **5/6 (수)** | 핵심 로직 | — | 1주치 데이터, 필터 함수 | 1주치 데이터, 수면·활동 집계 | 1주치 데이터, 추론 노드 연결 | 페르소나 톤·격려 멘트, 스케줄 도출 로직 | 운동→부위 매핑, 누적 피로도 계산 |
| **5/7 (목)** | 멀티턴 | — | 일정 충돌 케이스 데이터 | 야근/피로 케이스 데이터 | 메모리 노드 연결 | 체크포인터, 재조정 프롬프트 | 멀티턴 입력창, 부위별 색상 단계화 |
| **5/8 (금)** | **1차 통합 ★** | end-to-end 1회 성공 (입력→응답→화면) | UI에 일정 카드 실연결 | UI에 건강 카드 실연결 | 실제 LLM 호출, 응답 포맷 검증 | 프롬프트 튜닝 | 모든 컴포넌트 모아 메인 화면 완성, 승인 버튼 |
| **5/9 (토)** | 통합 테스트 | 시나리오 5개 통과 | 빈시간 없는 주 데이터 | 컨디션 변동 데이터 | 그래프 디버깅 | 멀티턴 안정화 | 이미지 캐시·로딩 상태·에러 핸들링 |
| **5/10 (일)** | **코드 동결** | 데모 시나리오 무사고 시연 1회, 태그 `v1.0-demo` | 데모 데이터 점검 | 데모 데이터 점검 | 데모 입력 회귀 | 데모 멘트 점검 | 데모 화면 최종 점검 |

### 5/11~14 (발표 준비, 기획서 로드맵 그대로)
- 5/11~12: 발표 자료 작성, 데모 스크립트화, 화면 녹화/스크린샷
- 5/13~14: 내부 리허설, 피드백 반영, 데모 환경 최종 점검
- 5/15: 발표

---

## 4. 검증 (각 마일스톤 종료 시 체크)

- **5/4 EOD**: `schemas/models.py`가 main에 머지, 5명 모두 자기 슬라이스의 빈 함수/스텁이 main에 올라와 있는가. 전원 LangGraph 튜토리얼 1회 완주.
- **5/5 EOD**: 각 슬라이스가 더미 입력으로 단독 실행되는가 (`python -m <slice>` 또는 단위 테스트 1개).
- **5/8 EOD**: Streamlit 실행 → 사용자 입력 → Agent 응답 → 화면 출력의 **end-to-end 1회 성공**.
- **5/9 EOD**: 기획서 KPI 시나리오 5개 통과
  1. 일정 충돌률 1% 미만 (10회 생성 시 충돌 0회)
  2. 피로도 높음 부위에 해당 운동 추천 0회
  3. 빈 시간 없는 주에 10분 대체 루틴 제안
  4. 멀티턴 재조정 ("화요일은 너무 피곤할 것 같아") 정상 반영
  5. 이미지가 추천 일정의 부위와 일관되게 변화
- **5/10 EOD**: 데모 시나리오 스크립트대로 무사고 시연 1회.

---

## 5. 기술 스택 요약

- **언어**: Python 3.11+
- **LLM**: OpenAI GPT-4o
- **Agent 프레임워크**: LangGraph (+ LangChain 기본 도구)
- **UI**: Streamlit (`st.chat_message`, `streamlit-calendar` 또는 dataframe)
- **이미지**: Pillow + 사전 제작 SVG 오버레이 합성 (안전), 또는 이미지 모델 호출 (도전)
- **데이터**: 로컬 JSON 파일 (가상)
- **메모리**: LangGraph 체크포인터 (in-memory or SQLite)

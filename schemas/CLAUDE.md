# schemas/ — 공통 데이터 모델

> **담당**: 전원이 import. 변경은 데일리 싱크 합의 후 한 PR로만.

## 역할

5개 슬라이스의 **인터페이스 계약**. 모든 모듈은 자기 디렉토리에서 `from schemas import ...`로 import한다. 이 파일이 바뀌면 전원의 코드가 영향받으므로 단독 결정 금지.

## 모델 (Pydantic v2)

| 모델 | 용도 | 생성/소비 |
|---|---|---|
| `CalendarEvent` | 사용자 일정 1건 | `tools.get_calendar` → Agent |
| `HealthSnapshot` | 1일치 수면·활동량·HR | `tools.get_health` → Agent |
| `WorkoutRecord` | 과거 운동 1건 | `tools.get_workouts` → Agent |
| `WorkoutSlot` | 추천 운동 1건 | Agent → UI |
| `MuscleFatigueState` | 1일치 부위별 피로도 | Agent → `visuals.render_fatigue` |
| `ScheduleProposal` | 슬롯 + 피로도 타임라인 묶음 | Agent → UI |
| `AgentResponse` | 챗 응답 + 제안 + 승인 필요 여부 | `run_agent` → Streamlit |

## 변경 절차

1. 데일리 싱크에서 변경안 공유 (왜 필요한지 이유 포함)
2. 합의되면 `models.py` + 영향받는 모든 호출부를 **하나의 PR**에 묶어 수정
3. 머지 직후 슬랙/카톡 공지

## 작업 시 주의

- `Field(ge=, le=)`로 범위 제약을 모델에 박아두기 — 호출 측에서 검증 안 해도 됨
- `int | None = None`처럼 PEP 604 union 사용 (Python 3.11+)
- 새 필드는 **기본값 있는 옵셔널**로 추가하면 호환성 유지에 좋음
- 직렬화 출력은 `model.model_dump(mode="json")` 사용 (Streamlit `st.json` 호환)

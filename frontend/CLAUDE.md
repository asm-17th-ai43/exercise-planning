# frontend/ — Flutter Web 클라이언트

> **담당**: A(노준영) 주담당. B(박장우)는 `lib/chat/` 협업.

## 역할

데모 메인 화면 — 좌측 카드 3종(이번 주 일정 / 컨디션 점수 / 최근 운동 이력) + 가운데 부위별 피로도 레이더 + 우측 AI 코치 채팅. `docs/design/ChatGPT Image 2026년 5월 4일 오전 01_17_14.png` 참고.

## 디렉토리 분담 (예정)

| 경로 | 책임 | 슬라이스 |
|---|---|---|
| `lib/main.dart`, 레이아웃, 라우팅 | 전체 셸 | A |
| `lib/cards/` (calendar/health/workouts/fatigue) | 좌·중앙 패널 | A |
| `lib/api/` (REST 클라이언트) | `/data/*` 호출 + 모델 디코드 | A |
| `lib/chat/` (채팅 UI, SSE 클라이언트) | 우측 패널, 스트림 | B |

A와 B는 같은 Flutter 앱 안에서 디렉토리 단위로 분리. PR은 디렉토리 단위로 작게.

## 백엔드 합의

- **호스트(개발)**: `http://localhost:8000` (FastAPI uvicorn)
- **REST**: `/data/calendar`, `/data/health`, `/data/workouts` — `schemas/models.py`의 Pydantic 모델 1:1 매핑
- **SSE**: `POST /agent/chat`. `ChatChunk` 시퀀스 (`type` ∈ text/tool_call/proposal/done/error)
- 모델/엔드포인트 변경은 데일리 싱크 합의 후 `schemas/CLAUDE.md` 갱신과 함께만

## 셋업 (A가 5/5에 실행)

```bash
cd frontend
flutter create .         # 현재 디렉토리에 Flutter Web 프로젝트 생성
flutter run -d chrome    # 로컬에서 띄우기
```

`flutter create .`이 생성하는 기본 파일들은 main에 머지 가능 (CLAUDE.md, .gitkeep만 보존하면 충돌 없음).

## 작업 시 주의

- UI 텍스트는 한국어. 식별자·주석·로그는 영어.
- `dart run build_runner` 등 코드 생성 도구 도입 시 데일리 싱크 공지.
- BE가 401/501 등 stub을 돌려줄 수 있음 — UI 로딩/에러 상태를 처음부터 설계.
- 디자인: `docs/design/ChatGPT Image 2026년 5월 4일 오전 01_17_14.png` 톤 유지. 색맹 친화 팔레트.

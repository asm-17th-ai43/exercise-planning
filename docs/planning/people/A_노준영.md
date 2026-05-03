# A — 노준영 (Flutter Web 프론트)

## 한 줄 책임

Flutter Web 대시보드 — 좌측 카드 3종(일정/컨디션/최근 운동) + 가운데 부위별 피로도 레이더. BE와 `/data/*` REST 합의 + UI 조립.

## 주 디렉토리·파일

- `frontend/` 전체 (B의 `lib/chat/` 제외)
- `frontend/lib/main.dart` — 레이아웃, 라우팅
- `frontend/lib/cards/` — calendar / health / workouts / fatigue 위젯
- `frontend/lib/api/` — REST 클라이언트 (`/data/*`)
- `frontend/test/` — Dart 단위 테스트

## 합의 책임 (5/4 락)

- **D/E와**: `/data/calendar`, `/data/health`, `/data/workouts` REST 응답 형태. 시그니처는 `schemas/models.py` Pydantic 모델 그대로.
- **B와**: `frontend/` 디렉토리 컨벤션 (B는 `lib/chat/` 안에서 작업, A는 그 외). 레이아웃 셸이 채팅 영역에 어떤 폭/위치를 줄지.

## 일자별 to-do

| 날짜 | 할 일 | 합격 기준 |
|---|---|---|
| **5/4 (월)** | `cd frontend && flutter create .` 실행 / 빈 화면 1회 띄움 (`flutter run -d chrome`) / 첫 PR | 빈 Flutter Web 화면 떠 있음 |
| **5/5 (화)** | 좌측 카드 1종(예: 일정 카드) 더미 데이터로 렌더 + `lib/api/getCalendar()` REST 클라이언트 1개 | BE에서 받은 더미 일정이 카드에 표시 |
| **5/6 (수)** | 좌측 카드 3종 + 가운데 피로도 레이더 모두 실데이터 연동 | 좌·중앙 4종 위젯이 BE 실데이터로 갱신 |
| **5/7 (목)** | 카드 로딩/에러 상태, 색상 단계화 (피로도 0=초록 → 5=빨강) | 네트워크 지연/501 에러 시 UI 깨지지 않음 |
| **5/8 (금)** ★ | 화면 전체 조립, BE 실연결 검증 | 채팅에 "이번 주 운동 추천해줘" → 카드 3종 + 추천 슬롯 + 레이더 모두 출력 |
| **5/9 (토)** | 화면 폴리싱 (여백, 폰트, 색맹 친화), 로딩/에러 표시 | 디자인 톤이 `docs/design/*.png`와 일치 |
| **5/10 (일)** | 데모 화면 최종 점검 (해상도, 컬러, 로딩) | 데모 시나리오 무사고 시연 |

## KPI 시나리오 — 본인 영향

- **5번** (추천 부위와 FE 레이더 색상 일치) — 레이더 위젯이 `MuscleFatigueState.fatigue`를 색으로 정확히 변환하는지

## 자주 볼 문서·CLAUDE.md

- `frontend/CLAUDE.md` ← 본인 슬라이스
- `schemas/CLAUDE.md` ← REST 응답 모델
- `backend/CLAUDE.md` ← 호출할 엔드포인트
- `docs/spec/feature_spec.md` ← F1·F2·F3·F5 수용 기준
- `docs/design/ChatGPT Image *.png` ← 디자인 레퍼런스

## 흔한 함정

- BE가 501을 돌려줘도 UI 로딩 상태로 화면을 먼저 그릴 것 (mock-first)
- `flutter create .` 실행 시 기존 `CLAUDE.md`와 `.gitkeep`은 보존됨 (덮어쓰지 않음)
- UI 텍스트는 한국어, 식별자·로그는 영어
- Flutter Web의 CORS — BE가 `localhost:*` 허용으로 설정됨 (`backend/main.py`)

cat > README.md <<'EOF'
# Meeting Action AI

회의 transcript JSON을 기반으로 회의 발화를 정제하고, 액션아이템을 구조화하여 SQLite에 저장한 뒤 Streamlit 대시보드로 확인할 수 있는 PoC 프로젝트입니다.

본 프로젝트는 회의록 자동 정리보다 액션아이템 누락 방지와 추적 가능성 확보를 우선 목표로 설계했습니다.

## 1. 프로젝트 목표

모비데이즈의 광고주 캠페인 회의에서는 회의 후 담당자가 회의록과 액션아이템을 수기로 정리해야 합니다. 이 과정에서 다음 문제가 발생할 수 있습니다.

- 회의 후 정리 작업에 30~60분 소요
- 한국어 회의 특성상 담당자와 기한이 암묵적으로 표현됨
- 액션아이템이 누락되거나 후속 관리가 어려움
- LLM 결과를 그대로 신뢰하기 어려움

본 PoC는 transcript JSON을 입력으로 받아 다음 흐름을 구현합니다.

transcript JSON
→ 발화 단위 변환
→ 전처리
→ SQLite 적재
→ 액션아이템 구조화
→ Pydantic 스키마 검증
→ Slack payload 생성
→ Streamlit 대시보드 시각화

## 2. 기술 스택

- Python: 전체 파이프라인 구현
- pandas: transcript 처리 및 DataFrame 변환
- SQLite: 로컬 PoC용 데이터 저장소
- Pydantic: 액션아이템 스키마 검증
- Streamlit: 분석 대시보드 구현

SQLite를 선택한 이유는 샘플 데이터 기반 PoC에서 별도 서버 구축 없이 재현 가능한 실행 환경을 만들기 위해서입니다. 사내 약 100명 규모의 초기 검증 단계에서는 SQLite 기반 로컬 PoC로도 데이터 흐름과 검증 구조를 충분히 설명할 수 있다고 판단했습니다.

## 3. 프로젝트 구조

meeting-action-ai/
├── app/
│   └── dashboard.py
├── data/
│   ├── raw/
│   │   ├── ko_meeting_3speakers.json
│   │   └── ko_meeting_3speakers_4min_faster.mp3
│   └── processed/
│       └── meeting_ai.db
├── outputs/
│   └── slack_payload_sample.json
├── prompts/
│   └── action_item_prompt.md
├── src/
│   ├── database.py
│   ├── extract_actions.py
│   ├── ingest.py
│   ├── preprocess.py
│   ├── schema.py
│   └── slack_payload.py
├── AI_USAGE.md
├── README.md
├── main.py
└── requirements.txt

## 4. 실행 방법

전체 파이프라인과 대시보드는 다음 명령으로 실행할 수 있습니다.

make run

### 1) 패키지 설치

pip install -r requirements.txt

### 2) 파이프라인 실행

python main.py

### 3) 대시보드 실행

streamlit run app/dashboard.py



## 5. 데이터 파이프라인

### 입력

제공된 transcript JSON을 사용합니다.

data/raw/ko_meeting_3speakers.json

### 처리 과정

1. ingest.py
   - transcript JSON 로드
   - segment 단위 발화를 DataFrame으로 변환
   - meeting_id, utterance_id, speaker, role, text_raw 생성

2. preprocess.py
   - 화자명 정규화
   - 머뭇거림 및 불필요 표현 제거
   - 광고, 마케팅 약어 사전 적용

3. database.py
   - meetings, utterances, action_items 테이블 생성
   - SQLite DB에 적재
   - 재실행 시 replace 방식으로 중복 적재 방지

4. extract_actions.py
   - PoC 단계에서는 transcript 기반 mock action item 생성
   - 실제 LLM 호출 모듈로 교체 가능한 구조로 분리

5. schema.py
   - Pydantic 기반 ActionItem 스키마 검증
   - status, priority, confidence 범위 검증

6. slack_payload.py
   - Slack 메시지 전송용 JSON payload 생성

## 6. 데이터 스키마

### meetings

회의 단위 메타데이터를 저장합니다.

- meeting_id
- client_name
- campaign_name
- language
- speaker_count
- segment_count

### utterances

원문 발화와 정제 발화를 저장합니다.

- utterance_id
- meeting_id
- line_no
- speaker
- speaker_norm
- role
- text_raw
- text_clean
- text_for_llm
- client_name
- campaign_name

### action_items

구조화된 액션아이템을 저장합니다.

- action_id
- meeting_id
- owner
- owner_role
- task
- due_date
- status
- priority
- confidence
- source_utterance_ids
- reason

source_utterance_ids를 저장한 이유는 액션아이템이 어떤 원문 발화에서 추출되었는지 추적하기 위해서입니다. 이를 통해 LLM 또는 추출 로직의 결과를 사람이 검토할 수 있습니다.

## 7. LLM 프롬프트 설계

프롬프트는 prompts/action_item_prompt.md에 정리했습니다.

주요 설계 기준은 다음과 같습니다.

- 광고 도메인 컨텍스트 제공
- CPM, ROAS, GA, A/B, CTA 등 약어 설명
- 한국어 회의의 암묵적 R&R 표현 처리
- JSON array 출력 강제
- confidence 정책 정의
- source utterance 기반 근거 추적
- few-shot 예시 제공

본 PoC에서는 외부 유출 금지 조건을 고려하여 실제 원천 회의 데이터를 외부 API로 전송하지 않고, mock extraction 방식으로 결과를 생성했습니다. 실제 운영 환경에서는 사내 보안 정책에 맞는 LLM 또는 로컬 모델을 연결할 수 있도록 모듈을 분리했습니다.

## 8. 대시보드 구성

Streamlit 대시보드는 다음 위젯을 제공합니다.

1. 주차별 회의 및 액션아이템 발생 추이
2. 담당자별 미완료 액션아이템 Top N
3. 캠페인 및 광고주별 반복 이슈 키워드
4. Confidence 분포 및 저신뢰 항목 드릴다운
5. 전체 액션아이템 테이블
6. 원문 발화 데이터 테이블

의사결정자는 대시보드를 통해 담당자별 업무 쏠림, 반복적으로 발생하는 캠페인 이슈, 사람이 검토해야 할 저신뢰 액션아이템을 확인할 수 있습니다.

## 9. 멱등성

파이프라인은 재실행 시 같은 결과를 유지하도록 설계했습니다.

- utterances 테이블은 if_exists="replace" 방식으로 저장
- action_items 테이블도 재생성 방식으로 저장
- 동일 transcript를 반복 실행해도 중복 row가 누적되지 않음

운영 환경에서는 meeting_id, utterance_id, action_id 기준 upsert 방식으로 확장할 수 있습니다.

## 10. 실패 시나리오 및 대응

### 1) 담당자 또는 기한이 암묵적으로 표현되는 경우

예: “그건 제가 챙길게요”

대응:
- 현재 발화자의 speaker와 role을 owner로 추정
- confidence를 낮게 부여
- source_utterance_ids를 함께 저장해 사람이 검토 가능하게 함

### 2) LLM이 존재하지 않는 액션아이템을 생성하는 경우

대응:
- source_utterance_ids 필수화
- Pydantic 스키마 검증 적용
- confidence 기준으로 저신뢰 항목을 대시보드에서 드릴다운

### 3) 마케팅 약어를 잘못 해석하는 경우

대응:
- 전처리 단계에서 GA, CTA, A/B, Meta, Pixel 등 약어 사전을 적용
- 프롬프트에도 도메인 컨텍스트를 명시

## 11. 향후 개선 방향

- Gemini 또는 로컬 LLM 기반 실제 action item extraction 연결
- local Whisper 기반 STT 처리 추가
- 액션아이템 진행상황 업데이트 루프 구현
- 유사 회의 및 과거 결정 검색 기능 추가
- precision, recall 기반 추출 품질 평가 코드 추가

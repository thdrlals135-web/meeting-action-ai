# Meeting Action AI 기획안

## 1. 문제 재정의

모비데이즈의 광고주 캠페인 회의에서는 회의 후 담당자가 회의록을 정리하고, 그 안의 액션아이템을 별도 트래킹 시스템에 옮기는 작업이 반복된다. 이 과정에서 단순 정리 시간뿐 아니라 액션아이템 누락, 담당자 불명확, 기한 미정, 후속 관리 실패 문제가 발생할 수 있다.

본 PoC는 회의록을 예쁘게 요약하는 것보다, 회의 발화를 실행 가능한 업무 데이터로 전환하는 데 초점을 둔다. 특히 한국어 회의에서는 “제가 챙길게요”, “이따 슬랙으로 정리하죠”, “금요일까지면 될 것 같긴 한데”처럼 책임자와 기한이 암묵적으로 표현되는 경우가 많다. 따라서 단순 요약보다 담당자, 업무, 기한, 우선순위, 신뢰도, 원문 근거를 구조화하는 것이 더 중요하다고 판단했다.

우선 해결할 페인포인트는 다음과 같다.

- 회의 후 30~60분 소요되는 수기 정리 시간 감소
- 암묵적으로 지나가는 액션아이템 누락 방지
- 담당자별 미완료 업무 쏠림 확인
- LLM 추출 결과를 사람이 검토 가능한 데이터로 관리
- 원문 발화 근거를 남겨 추적 가능성 확보

따라서 본 시스템은 회의 transcript JSON을 입력으로 받아 발화 단위 정제, 액션아이템 구조화, 스키마 검증, Slack payload 생성, 대시보드 시각화까지 연결하는 작은 end-to-end 데이터·AI 파이프라인으로 설계했다.

---

## 2. 시스템 아키텍처

전체 흐름은 다음과 같다.

회의 음성 또는 transcript JSON
→ Ingest
→ Preprocess
→ SQLite 저장
→ Action Item Extraction
→ Pydantic Validation
→ Slack Payload 생성
→ Streamlit Dashboard

### 2.1 수집 단계

제공된 transcript JSON을 기본 입력으로 사용했다. 음성 파일 기반 STT도 가능하지만, 본 과제의 핵심은 STT 자체보다 데이터 파이프라인 설계, LLM 출력 구조화, 검증 로직, 대시보드 의사결정 흐름이라고 판단했다. 따라서 speaker, role, text가 포함된 transcript JSON을 우선 사용하여 필수 요구사항을 안정적으로 구현했다.

### 2.2 전처리 단계

전처리에서는 다음 작업을 수행한다.

- 화자명 정규화
- 머뭇거림, 불필요 표현 제거
- 광고·마케팅 약어 사전 적용
- LLM 입력용 text_for_llm 컬럼 생성

예를 들어 GA, CTA, A/B, Meta, Pixel과 같은 약어는 회의에서 자주 등장하지만 LLM 또는 후속 분석에서 의미가 모호해질 수 있다. 따라서 전처리와 프롬프트 양쪽에 도메인 컨텍스트를 반영했다.

### 2.3 저장 단계

SQLite를 사용해 meetings, utterances, action_items 테이블을 구성했다. SQLite를 선택한 이유는 별도 서버 없이 실행 가능하고, GitHub Codespaces 환경에서 재현성이 높기 때문이다. 사내 100명 사용 전 초기 PoC 단계에서는 데이터 흐름 검증과 대시보드 구현에 충분하다고 판단했다.

### 2.4 액션아이템 추출 단계

본 PoC에서는 외부 유출 금지 조건을 고려해 실제 회의 원문을 외부 API로 전송하지 않고, transcript 기반 mock extraction을 사용했다. 다만 모듈 구조는 실제 LLM 호출로 교체 가능하도록 분리했다.

액션아이템에는 다음 필드를 포함했다.

- owner
- owner_role
- task
- due_date
- status
- priority
- confidence
- source_utterance_ids
- reason

핵심은 confidence와 source_utterance_ids다. LLM 결과를 그대로 신뢰하지 않고, 사람이 어떤 원문 발화를 근거로 추출되었는지 확인할 수 있도록 설계했다.

### 2.5 검증 단계

Pydantic 기반 ActionItem 스키마를 정의했다. 이를 통해 status, priority, confidence 범위, 필수 필드 누락 여부를 검증한다. 스키마를 통과하지 못한 항목은 needs_review 상태로 전환할 수 있도록 설계했다.

### 2.6 분배 및 분석 단계

Slack payload JSON을 생성해 실제 업무 알림 시스템으로 확장할 수 있게 했다. 또한 Streamlit 대시보드에서는 주차별 추이, 담당자별 미완료 액션아이템, 반복 이슈 키워드, confidence 분포와 저신뢰 항목을 확인할 수 있다.

---

## 3. 데이터 스키마 설계 근거

본 PoC의 핵심 설계 방향은 원문 추적성과 업무 활용성의 균형이다.

### 3.1 meetings

회의 단위 메타데이터를 저장한다.

- meeting_id
- client_name
- campaign_name
- language
- speaker_count
- segment_count

회의별 분석, 주차별 회의 수 집계, 캠페인별 대시보드 확장을 위해 별도 테이블로 분리했다.

### 3.2 utterances

발화 단위 데이터를 저장한다.

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

utterances 테이블을 별도로 둔 이유는 액션아이템이 추출된 근거를 원문 발화 단위로 추적하기 위해서다. LLM이 잘못된 업무를 생성했을 때 source_utterance_ids를 통해 사람이 바로 검토할 수 있다.

### 3.3 action_items

실행 가능한 업무 단위 데이터를 저장한다.

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

action_items는 Slack, Notion, Jira와 같은 외부 트래킹 시스템으로 보내기 쉽도록 일부 비정규화했다. owner, owner_role, task, due_date를 한 테이블에 두면 대시보드 집계와 업무 분배가 단순해진다.

### 3.4 정규화와 비정규화 판단

회의 원문은 utterances에 정규화해 저장하고, 실제 업무 실행에 필요한 정보는 action_items에 비정규화해 저장했다. 이는 분석과 운영을 동시에 고려한 구조다.

- 원문 추적성: utterances, source_utterance_ids
- 업무 실행성: action_items
- 대시보드 집계 편의성: owner, priority, confidence 직접 저장

---

## 4. Before / After 임팩트 추정

본 PoC는 회의록 정리 전체를 완전히 대체하기보다, 회의 후 액션아이템 초안 생성과 검토 우선순위 제공을 목표로 한다.

### 4.1 Before

기존 방식에서는 회의 후 담당자가 다음 작업을 수기로 수행해야 한다.

- 회의록 정리
- 액션아이템 식별
- 담당자와 기한 확인
- 슬랙 또는 트래킹 시스템에 옮겨 적기
- 누락 항목 재확인

회의 1건당 약 30~60분이 소요된다고 가정할 수 있다.

### 4.2 After

도입 후에는 시스템이 1차 초안을 자동 생성한다.

- transcript JSON 정제
- 액션아이템 후보 생성
- confidence 및 원문 근거 제공
- Slack payload 생성
- 대시보드에서 저신뢰 항목 검토

담당자는 전체 회의록을 처음부터 다시 읽는 대신, confidence가 낮은 항목과 담당자·기한이 불명확한 항목을 우선 검토하면 된다.

### 4.3 100명 조직 기준 추정

사내 약 100명 사용 환경에서 주 50건의 캠페인 회의가 발생한다고 가정한다.

기존 방식:
- 회의 1건당 30~60분
- 주 50건 기준 25~50시간 소요

도입 후:
- 자동 초안 생성 1~3분
- 담당자 검토 5~10분
- 주 50건 기준 약 5~10시간 검토

따라서 주당 약 20~40시간의 정리 업무를 줄일 수 있다. 또한 시간 절감뿐 아니라 담당자 누락, 기한 누락, 후속 조치 지연을 줄이는 품질 개선 효과도 기대할 수 있다.

### 4.4 대시보드 기반 운영 효과

대시보드는 단순 차트 나열이 아니라 운영 의사결정을 지원하도록 구성했다.

- 담당자별 미완료 액션아이템: 특정 담당자에게 업무가 몰리는지 확인
- 반복 이슈 키워드: 캠페인 준비 과정의 병목 확인
- confidence 분포: 사람이 검토해야 할 항목 우선순위화
- 원문 발화 데이터: 추출 근거 검증

---

## 5. 실패 시나리오 및 대응

### 5.1 실패 시나리오 1: 암묵적 R&R로 담당자가 불명확한 경우

예시:
- “그건 제가 챙길게요”
- “이따 슬랙으로 정리하죠”
- “컨펌은 내가 받기로 한 거 맞죠?”

문제:
한국어 회의에서는 주어가 생략되거나, 이전 발화 맥락을 기반으로 담당자가 결정되는 경우가 많다. 이 경우 LLM이 담당자를 잘못 지정할 수 있다.

대응:
- speaker_norm과 role을 함께 저장
- 현재 발화자를 owner로 추정하는 규칙 적용
- confidence를 낮게 부여
- source_utterance_ids를 저장해 사람이 검토 가능하게 함
- owner 추정이 불가능하면 needs_review 처리

### 5.2 실패 시나리오 2: LLM이 존재하지 않는 액션아이템을 생성하는 경우

문제:
LLM은 회의 맥락을 과도하게 해석해 실제로 결정되지 않은 업무를 생성할 수 있다. 이는 실무에서 잘못된 업무 지시로 이어질 수 있다.

대응:
- JSON schema 기반 출력 강제
- Pydantic 검증 적용
- source_utterance_ids 필수화
- 원문 근거가 없는 항목은 제거하거나 needs_review 처리
- 대시보드에서 confidence 낮은 항목을 우선 검토

### 5.3 실패 시나리오 3: 광고·마케팅 약어 오해

예시:
- GA
- CTA
- A/B
- Pixel
- Meta

문제:
약어가 전처리 없이 LLM에 전달되면 업무 의미가 흐려질 수 있다. 예를 들어 Pixel은 디자인 요소가 아니라 전환 추적 이벤트와 연결될 수 있다.

대응:
- 전처리 단계에서 약어 사전 적용
- 프롬프트에 도메인 glossary 제공
- text_raw와 text_for_llm을 모두 저장해 원문과 보강 입력을 함께 확인 가능하게 함

### 5.4 실패 시나리오 4: 파이프라인 재실행 시 중복 적재

문제:
회의 데이터를 반복 실행할 때 같은 발화와 액션아이템이 중복 저장되면 대시보드 지표가 왜곡된다.

대응:
- meeting_id, utterance_id, action_id를 고정 키로 설계
- PoC에서는 replace 방식으로 테이블 재생성
- 운영 환경에서는 upsert 방식으로 확장 가능

---

## 6. 향후 개선 계획

본 PoC의 다음 개선 방향은 다음과 같다.

1. 실제 LLM API 또는 사내 보안 환경의 LLM 연결
2. local Whisper 기반 STT 처리 추가
3. Slack 또는 Notion 기반 액션아이템 상태 업데이트 루프 구현
4. 유사 회의 및 과거 결정 검색 기능 추가
5. precision, recall 기반 추출 품질 평가 코드 추가
6. 주차별 실제 회의 데이터 누적 후 병목 트렌드 분석 고도화

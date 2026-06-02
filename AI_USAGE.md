# AI Usage

본 프로젝트는 AI 도구를 활용하여 과제 요구사항을 빠르게 구조화하고, 데이터 파이프라인과 LLM 출력 검증 설계를 보완했습니다.

## 1. 사용한 AI 도구

- ChatGPT
- GitHub Codespaces
- GitHub Copilot 또는 VS Code 코드 제안 기능

## 2. AI 도구 사용 목적

AI 도구는 단순 코드 자동 생성이 아니라 다음 목적에 활용했습니다.

1. 과제 요구사항 분해
   - 회의록 자동 정리, 액션아이템 추출, 저장소 적재, 대시보드 구현 요구사항을 단계별 작업으로 분해했습니다.

2. 프로젝트 구조 설계
   - ingest, preprocess, database, extract_actions, schema, slack_payload, dashboard 모듈로 역할을 분리했습니다.
   - 단일 스크립트가 아니라 재실행 가능한 작은 데이터 파이프라인 형태로 구성했습니다.

3. LLM 출력 안정화 설계
   - LLM 결과를 그대로 저장하지 않고 Pydantic 스키마로 검증하는 구조를 설계했습니다.
   - confidence, source_utterance_ids, reason 필드를 추가하여 사람이 검토할 수 있는 근거를 남기도록 했습니다.

4. README 및 프롬프트 문서화
   - 평가자가 시스템 흐름과 의사결정 근거를 빠르게 이해할 수 있도록 README와 프롬프트 문서를 정리했습니다.

## 3. 주요 프롬프트 활용 방식

AI에게 다음과 같은 방식으로 질문했습니다.

- "회의 transcript JSON 기반으로 어떤 데이터 파이프라인을 먼저 구현해야 하는가"
- "SQLite에 저장할 테이블 구조를 어떻게 나누는 것이 좋은가"
- "LLM 액션아이템 추출 결과를 신뢰 가능한 데이터로 만들려면 어떤 필드가 필요한가"
- "Streamlit 대시보드에서 과제 요구사항 4개 위젯을 어떻게 구성해야 하는가"
- "AI_USAGE.md와 README.md에 어떤 내용을 포함해야 하는가"

## 4. AI 결과물을 그대로 사용하지 않고 수정한 판단 사례

### 1) STT 직접 구현 대신 transcript JSON 우선 사용

초기에는 로컬 Whisper 기반 STT를 적용하는 방향도 검토했지만, 과제의 핵심은 STT 자체보다 데이터 파이프라인, 액션아이템 구조화, LLM 출력 검증이라고 판단했습니다.

따라서 제공된 transcript JSON을 우선 사용하여 end-to-end 흐름을 먼저 완성했습니다.

판단 이유:
- 제한된 시간 내 필수 요구사항 완성이 더 중요함
- transcript JSON에 이미 speaker, role, text가 포함되어 있어 파이프라인 검증에 충분함
- STT는 선택 가산점이므로 후순위 개선 항목으로 분리하는 것이 합리적임

### 2) 실제 LLM API 호출 대신 mock extraction 기본 경로 사용

외부 유출 금지 조건을 고려하여 원천 회의 데이터를 외부 SaaS 또는 공개 API로 전송하지 않았습니다.

대신 transcript를 기반으로 검증 가능한 mock action item을 생성하고, 실제 운영 시 LLM 모듈로 교체 가능한 구조로 설계했습니다.

판단 이유:
- 과제 조건상 광고주 정보가 포함된 원천 데이터 외부 전송이 제한됨
- 실제 LLM 호출보다 스키마 검증, confidence, source utterance 추적 구조가 평가 핵심이라고 판단함
- mock 데이터라도 source_utterance_ids와 reason을 포함해 추적 가능성을 확보함

### 3) SQLite 선택

DuckDB와 Postgres도 고려했지만, PoC 단계에서는 SQLite를 선택했습니다.

판단 이유:
- 별도 서버 없이 실행 가능
- GitHub Codespaces 환경에서 재현이 쉬움
- 샘플 회의 1건 기반 검증에는 충분함
- 사내 100명 사용 전 초기 PoC로 데이터 흐름과 대시보드 검증에 적합함

### 4) action_items 테이블에 비정규화 필드 포함

owner, owner_role, task, due_date, priority, confidence, source_utterance_ids를 action_items 테이블에 직접 저장했습니다.

판단 이유:
- Slack, Notion, Jira 등 외부 업무 트래킹 시스템으로 분배하기 쉬움
- 대시보드에서 담당자별 미완료 액션아이템을 바로 집계할 수 있음
- source_utterance_ids를 통해 원문 근거 추적 가능

## 5. 컨텍스트 파일

AI 도구에 제공하거나 참고한 주요 컨텍스트는 다음과 같습니다.

- 과제 요구사항 전문
- 제공 transcript JSON 구조
- 구현 중 생성한 프로젝트 폴더 구조
- 각 모듈별 코드
- Streamlit 대시보드 실행 결과
- README 작성 요구사항
- LLM 프롬프트 설계 기준

## 6. AI 활용에 대한 최종 판단

본 프로젝트에서 AI는 단순히 코드를 대신 작성하는 도구가 아니라, 과제 요구사항을 구조화하고 기술 의사결정을 비교하는 보조 도구로 활용되었습니다.

최종 구현에서는 다음 기준으로 AI 결과물을 직접 검토하고 수정했습니다.

- 필수 요구사항을 충족하는가
- 재실행해도 결과가 중복 저장되지 않는가
- LLM 출력이 검증 가능한 데이터 구조로 저장되는가
- 사람이 저신뢰 항목을 검토할 수 있는가
- 대시보드가 단순 차트 나열이 아니라 의사결정 흐름을 보여주는가

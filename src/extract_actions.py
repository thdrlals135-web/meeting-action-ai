import json

import pandas as pd


def create_mock_action_items() -> pd.DataFrame:
    actions = [
        {
            "action_id": "act_001",
            "meeting_id": "meeting_001",
            "owner": "수아",
            "owner_role": "퍼포먼스 마케터",
            "task": "픽셀 이벤트 중복 발화 원인을 보정하고 성과 데이터를 다시 산출해 공유한다.",
            "due_date": "내일 오전",
            "status": "todo",
            "priority": "high",
            "confidence": 0.95,
            "source_utterance_ids": json.dumps(
                ["utt_005", "utt_009", "utt_029", "utt_030"],
                ensure_ascii=False,
            ),
            "reason": "성과 수치 불일치가 제안서 품질에 직접 영향을 주며, 담당자와 기한이 명확하게 언급됨.",
        },
        {
            "action_id": "act_002",
            "meeting_id": "meeting_001",
            "owner": "채린",
            "owner_role": "콘텐츠 디자이너",
            "task": "비주얼 카드 순서와 빈 슬롯 카피를 1차 정리한다.",
            "due_date": "내일 오전",
            "status": "todo",
            "priority": "medium",
            "confidence": 0.92,
            "source_utterance_ids": json.dumps(
                ["utt_017", "utt_032"],
                ensure_ascii=False,
            ),
            "reason": "담당자와 산출물이 명확하며, 내일 오전이라는 기한이 반복 확인됨.",
        },
        {
            "action_id": "act_003",
            "meeting_id": "meeting_001",
            "owner": "수아",
            "owner_role": "퍼포먼스 마케터",
            "task": "캠페인 세트 분리를 진행하고 광고주 컨펌 필요 사항을 정리한다.",
            "due_date": "수요일 오전",
            "status": "todo",
            "priority": "medium",
            "confidence": 0.90,
            "source_utterance_ids": json.dumps(
                ["utt_018", "utt_034"],
                ensure_ascii=False,
            ),
            "reason": "수아가 직접 수행하겠다고 언급했으며, 수요일 오전이라는 일정이 명시됨.",
        },
        {
            "action_id": "act_004",
            "meeting_id": "meeting_001",
            "owner": "지훈",
            "owner_role": "마케팅 팀장",
            "task": "광고주 담당자에게 신제품 누끼 컷 전달을 재요청한다.",
            "due_date": "오늘 안",
            "status": "todo",
            "priority": "high",
            "confidence": 0.94,
            "source_utterance_ids": json.dumps(
                ["utt_026", "utt_028", "utt_031"],
                ensure_ascii=False,
            ),
            "reason": "누끼 컷이 비주얼 작업의 선행 조건이며, 지훈이 직접 푸쉬하겠다고 언급함.",
        },
        {
            "action_id": "act_005",
            "meeting_id": "meeting_001",
            "owner": "채린",
            "owner_role": "콘텐츠 디자이너",
            "task": "메인 헤드라인, 랜딩 첫 화면, CTA 버튼 카피를 우선 수정한다.",
            "due_date": "금요일",
            "status": "todo",
            "priority": "high",
            "confidence": 0.88,
            "source_utterance_ids": json.dumps(
                ["utt_023", "utt_032"],
                ensure_ascii=False,
            ),
            "reason": "수정 대상은 명확하지만 금요일 일정은 다소 완곡하게 표현되어 confidence를 약간 낮게 설정함.",
        },
        {
            "action_id": "act_006",
            "meeting_id": "meeting_001",
            "owner": "수아",
            "owner_role": "퍼포먼스 마케터",
            "task": "CTA 변경 시 전환 추적 이벤트를 함께 확인한다.",
            "due_date": None,
            "status": "todo",
            "priority": "medium",
            "confidence": 0.86,
            "source_utterance_ids": json.dumps(
                ["utt_024", "utt_025", "utt_034"],
                ensure_ascii=False,
            ),
            "reason": "담당자는 명확하지만 구체적인 기한이 없어 due_date를 null로 둠.",
        },
        {
            "action_id": "act_007",
            "meeting_id": "meeting_001",
            "owner": "수아",
            "owner_role": "퍼포먼스 마케터",
            "task": "기존 A/B 테스트를 종료하고 변경된 카피 기준으로 다시 세팅한다.",
            "due_date": None,
            "status": "todo",
            "priority": "medium",
            "confidence": 0.84,
            "source_utterance_ids": json.dumps(
                ["utt_021", "utt_033"],
                ensure_ascii=False,
            ),
            "reason": "수아가 정리하겠다고 언급했으나 정확한 실행 시점은 명시되지 않음.",
        },
        {
            "action_id": "act_008",
            "meeting_id": "meeting_001",
            "owner": "지훈",
            "owner_role": "마케팅 팀장",
            "task": "캠페인 세트 분리와 채널 운영안에 대한 광고주 컨펌을 받는다.",
            "due_date": None,
            "status": "todo",
            "priority": "high",
            "confidence": 0.80,
            "source_utterance_ids": json.dumps(
                ["utt_019", "utt_035", "utt_036"],
                ensure_ascii=False,
            ),
            "reason": "지훈이 컨펌을 받기로 한 흐름은 확인되지만 회의 중 다소 암묵적으로 정리되어 confidence를 낮춤.",
        },
    ]

    return pd.DataFrame(actions)


from src.schema import ActionItem


def validate_action_items(actions: pd.DataFrame) -> pd.DataFrame:
    """
    추출된 액션아이템이 사전에 정의한 스키마를 만족하는지 검증한다.
    pandas에서 None이 NaN으로 변환되는 경우를 방지하기 위해
    검증 전 결측값을 명시적으로 None으로 정규화한다.
    """

    validated_rows = []

    for row in actions.to_dict(orient="records"):
        try:
            # pandas NaN 값을 Pydantic이 처리 가능한 None으로 변환
            for key, value in row.items():
                if pd.isna(value):
                    row[key] = None

            item = ActionItem(**row)
            validated_rows.append(item.model_dump())

        except Exception as e:
            row["status"] = "needs_review"
            row["confidence"] = 0.0
            row["reason"] = f"스키마 검증 실패: {str(e)}"
            validated_rows.append(row)

    return pd.DataFrame(validated_rows)
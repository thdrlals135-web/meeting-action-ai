import json
from pathlib import Path

import pandas as pd


def build_slack_payload(actions: pd.DataFrame) -> dict:
    """
    action_items DataFrame을 Slack 메시지 payload 형태로 변환한다.
    실제 Slack API 호출은 하지 않고, 전송 가능한 JSON 샘플만 생성한다.
    """

    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "노바드림 캠페인 회의 액션아이템 정리",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*총 액션아이템:* {len(actions)}개\n*검토 필요 항목:* {(actions['confidence'] < 0.85).sum()}개",
            },
        },
        {
            "type": "divider",
        },
    ]

    for _, row in actions.iterrows():
        due_date = row["due_date"] if pd.notna(row["due_date"]) else "미정"

        text = (
            f"*[{row['priority'].upper()}] {row['task']}*\n"
            f"- 담당자: {row['owner']} ({row['owner_role']})\n"
            f"- 기한: {due_date}\n"
            f"- Confidence: {row['confidence']}\n"
            f"- 근거 발화: {row['source_utterance_ids']}"
        )

        blocks.append(
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": text,
                },
            }
        )

    payload = {
        "channel": "#campaign-action-items",
        "username": "Meeting Action Bot",
        "text": "노바드림 캠페인 회의 액션아이템이 생성되었습니다.",
        "blocks": blocks,
    }

    return payload


def save_slack_payload(actions: pd.DataFrame, output_path: str):
    payload = build_slack_payload(actions)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    return payload
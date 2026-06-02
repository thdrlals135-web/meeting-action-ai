import json
from pathlib import Path

import pandas as pd


def load_transcript(json_path: str) -> dict:
    path = Path(json_path)

    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {json_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def transcript_to_utterances(data: dict) -> pd.DataFrame:
    rows = []

    for seg in data["segments"]:
        rows.append(
            {
                "meeting_id": "meeting_001",
                "utterance_id": f"utt_{int(seg['id']):03d}",
                "line_no": seg["line_no"],
                "speaker": seg["speaker"],
                "role": seg["role"],
                "text_raw": seg["text"],
                "language": data.get("language", "ko"),
                "client_name": "노바드림",
                "campaign_name": "다음달 캠페인 제안 사전 정렬 회의",
            }
        )

    return pd.DataFrame(rows)


if __name__ == "__main__":
    data = load_transcript("data/raw/ko_meeting_3speakers.json")
    df = transcript_to_utterances(data)

    print(df.head())
    print(f"총 발화 수: {len(df)}")
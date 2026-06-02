import re

import pandas as pd


FILLER_WORDS = [
    "어…",
    "음…",
    "어,",
    "음,",
    "아 ",
    "네,",
    "오케이",
    "그게,",
    "뭐…",
]


TERM_DICT = {
    "GA": "Google Analytics",
    "A/B": "A/B Test",
    "CTA": "Call To Action",
    "ROAS": "Return On Ad Spend",
    "CPM": "Cost Per Mille",
    "메타": "Meta",
    "인스타": "Instagram",
    "픽셀": "Pixel Tracking",
}


def normalize_speaker(speaker: str) -> str:
    speaker_map = {
        "지훈": "지훈",
        "수아": "수아",
        "채린": "채린",
    }
    return speaker_map.get(speaker, speaker)


def clean_text(text: str) -> str:
    cleaned = text

    for word in FILLER_WORDS:
        cleaned = cleaned.replace(word, "")

    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def apply_term_dictionary(text: str) -> str:
    converted = text

    for term, full_term in TERM_DICT.items():
        converted = converted.replace(term, f"{term}({full_term})")

    return converted


def preprocess_utterances(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    result["speaker_norm"] = result["speaker"].apply(normalize_speaker)
    result["text_clean"] = result["text_raw"].apply(clean_text)
    result["text_for_llm"] = result["text_clean"].apply(apply_term_dictionary)

    return result


def create_chunks(df: pd.DataFrame, chunk_size: int = 6) -> pd.DataFrame:
    """
    발화 순서를 기준으로 일정 개수 단위의 chunk를 생성한다.
    PoC 단계에서는 6개 발화 단위로 묶고,
    추후에는 topic shift나 embedding 기반 의미 chunking으로 확장할 수 있다.
    """
    result = df.copy()

    result["chunk_order"] = ((result["line_no"] - 1) // chunk_size) + 1
    result["chunk_id"] = result["chunk_order"].apply(
        lambda x: f"chunk_{int(x):03d}"
    )

    chunk_rows = []

    for chunk_id, group in result.groupby("chunk_id"):
        chunk_rows.append(
            {
                "chunk_id": chunk_id,
                "meeting_id": group["meeting_id"].iloc[0],
                "chunk_order": int(group["chunk_order"].iloc[0]),
                "start_utterance_id": group["utterance_id"].iloc[0],
                "end_utterance_id": group["utterance_id"].iloc[-1],
                "chunk_text": "\n".join(
                    [
                        f"{row['utterance_id']} | {row['speaker_norm']}({row['role']}): {row['text_for_llm']}"
                        for _, row in group.iterrows()
                    ]
                ),
            }
        )

    chunks = pd.DataFrame(chunk_rows)

    return result, chunks
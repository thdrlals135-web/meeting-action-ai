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
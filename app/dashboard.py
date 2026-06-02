import sqlite3
import re
from collections import Counter

import pandas as pd
import streamlit as st


DB_PATH = "data/processed/meeting_ai.db"


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)

    meetings = pd.read_sql_query("SELECT * FROM meetings", conn)
    utterances = pd.read_sql_query("SELECT * FROM utterances", conn)
    actions = pd.read_sql_query("SELECT * FROM action_items", conn)

    conn.close()

    return meetings, utterances, actions


def extract_issue_keywords(texts, top_n=10):
    stopwords = {
        "그", "이", "저", "좀", "것", "거", "수", "때", "일단", "그리고",
        "근데", "해서", "하면", "같아요", "있어요", "없어요", "봐야",
        "다시", "오늘", "내일", "오전", "정도", "같은데"
    }

    domain_keywords = [
        "픽셀", "GA", "메타", "전환", "CTA", "A/B", "랜딩", "카피",
        "비주얼", "유튜브", "인스타", "광고주", "컨펌", "누끼", "캠페인",
        "세트", "제안서", "헤드라인", "이벤트", "성과", "예산", "채널"
    ]

    joined = " ".join(texts)
    counts = Counter()

    for keyword in domain_keywords:
        counts[keyword] = joined.count(keyword)

    result = (
        pd.DataFrame(counts.items(), columns=["keyword", "count"])
        .query("count > 0")
        .sort_values("count", ascending=False)
        .head(top_n)
    )

    return result


st.set_page_config(
    page_title="Meeting Action Item Dashboard",
    layout="wide",
)

st.title("회의록 기반 액션아이템 추출 대시보드")

meetings, utterances, actions = load_data()

# 샘플 데이터에 날짜 컬럼이 없으므로 PoC 기준 회의일을 부여
meetings["meeting_date"] = "2026-06-01"
actions["meeting_date"] = "2026-06-01"

meetings["meeting_date"] = pd.to_datetime(meetings["meeting_date"])
actions["meeting_date"] = pd.to_datetime(actions["meeting_date"])

meetings["week"] = meetings["meeting_date"].dt.to_period("W").astype(str)
actions["week"] = actions["meeting_date"].dt.to_period("W").astype(str)

col1, col2, col3, col4 = st.columns(4)

col1.metric("회의 수", len(meetings))
col2.metric("발화 수", len(utterances))
col3.metric("액션아이템 수", len(actions))
col4.metric("평균 Confidence", round(actions["confidence"].mean(), 2))

st.divider()

st.subheader("1. 주차별 회의·액션아이템 발생 추이")

weekly_meetings = meetings.groupby("week").size().reset_index(name="meeting_count")
weekly_actions = actions.groupby("week").size().reset_index(name="action_item_count")

weekly_summary = pd.merge(
    weekly_meetings,
    weekly_actions,
    on="week",
    how="outer",
).fillna(0)

weekly_summary = weekly_summary.set_index("week")

st.bar_chart(weekly_summary)

st.caption(
    "의사결정 포인트: 특정 주차에 회의와 액션아이템이 동시에 증가하면 담당자 리소스 병목이나 캠페인 준비 부담이 커졌는지 확인할 수 있다."
)

st.subheader("2. 담당자별 미완료 액션아이템 Top N")

owner_counts = (
    actions[actions["status"] != "done"]
    .groupby("owner")
    .size()
    .reset_index(name="count")
    .sort_values("count", ascending=False)
)

st.bar_chart(owner_counts.set_index("owner"))

st.caption(
    "의사결정 포인트: 특정 담당자에게 액션아이템이 몰릴 경우 일정 조정이나 업무 재분배가 필요하다."
)

st.subheader("3. 캠페인 / 광고주별 반복 이슈 키워드")

keyword_df = extract_issue_keywords(utterances["text_clean"].tolist(), top_n=10)

if len(keyword_df) > 0:
    st.bar_chart(keyword_df.set_index("keyword"))
    st.dataframe(keyword_df, use_container_width=True)
else:
    st.info("추출된 반복 이슈 키워드가 없습니다.")

st.caption(
    "의사결정 포인트: 반복적으로 등장하는 이슈 키워드를 통해 캠페인 준비 과정에서 자주 막히는 병목을 파악할 수 있다."
)

st.subheader("4. LLM 추출 Confidence 분포 및 저신뢰 항목 드릴다운")

st.bar_chart(actions[["action_id", "confidence"]].set_index("action_id"))

threshold = st.slider("검토가 필요한 Confidence 기준", 0.0, 1.0, 0.85, 0.05)

low_confidence = actions[actions["confidence"] < threshold]

st.write(f"검토 필요 액션아이템 수: {len(low_confidence)}")

st.dataframe(
    low_confidence[
        [
            "action_id",
            "owner",
            "task",
            "due_date",
            "priority",
            "confidence",
            "reason",
            "source_utterance_ids",
        ]
    ],
    use_container_width=True,
)

st.caption(
    "의사결정 포인트: confidence가 낮은 항목은 담당자, 기한, 실행 여부가 불명확할 가능성이 높으므로 사람이 우선 검토한다."
)

st.divider()

st.subheader("전체 액션아이템")

st.dataframe(actions, use_container_width=True)

st.subheader("원문 발화 데이터")

st.dataframe(
    utterances[
        [
            "utterance_id",
            "speaker_norm",
            "role",
            "text_clean",
            "text_for_llm",
        ]
    ],
    use_container_width=True,
)
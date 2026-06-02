import sqlite3
from pathlib import Path

import pandas as pd


DB_PATH = "data/processed/meeting_ai.db"


def get_connection(db_path: str = DB_PATH):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(db_path)


def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id TEXT PRIMARY KEY,
            client_name TEXT,
            campaign_name TEXT,
            language TEXT,
            speaker_count INTEGER,
            segment_count INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS utterances (
            utterance_id TEXT PRIMARY KEY,
            meeting_id TEXT,
            line_no INTEGER,
            speaker TEXT,
            speaker_norm TEXT,
            role TEXT,
            text_raw TEXT,
            text_clean TEXT,
            text_for_llm TEXT,
            client_name TEXT,
            campaign_name TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS action_items (
            action_id TEXT PRIMARY KEY,
            meeting_id TEXT,
            owner TEXT,
            owner_role TEXT,
            task TEXT,
            due_date TEXT,
            status TEXT,
            priority TEXT,
            confidence REAL,
            source_utterance_ids TEXT,
            reason TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            chunk_id TEXT PRIMARY KEY,
            meeting_id TEXT,
            chunk_order INTEGER,
            start_utterance_id TEXT,
            end_utterance_id TEXT,
            chunk_text TEXT
        )
        """
    )

    conn.commit()


def upsert_meeting(conn, data: dict):
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR REPLACE INTO meetings (
            meeting_id,
            client_name,
            campaign_name,
            language,
            speaker_count,
            segment_count
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            "meeting_001",
            "노바드림",
            "다음달 캠페인 제안 사전 정렬 회의",
            data.get("language", "ko"),
            data.get("speaker_count"),
            data.get("segment_count"),
        ),
    )

    conn.commit()


def save_utterances(conn, df: pd.DataFrame):
    columns = [
        "utterance_id",
        "meeting_id",
        "line_no",
        "speaker",
        "speaker_norm",
        "role",
        "text_raw",
        "text_clean",
        "text_for_llm",
        "client_name",
        "campaign_name",
    ]

    df[columns].to_sql(
        "utterances",
        conn,
        if_exists="replace",
        index=False,
    )


def save_action_items(conn, df: pd.DataFrame):
    df.to_sql(
        "action_items",
        conn,
        if_exists="replace",
        index=False,
    )

def save_chunks(conn, df: pd.DataFrame):
    df.to_sql(
        "chunks",
        conn,
        if_exists="replace",
        index=False,
    )
from src.slack_payload import save_slack_payload
from src.database import (
    create_tables,
    get_connection,
    save_action_items,
    save_chunks,
    save_utterances,
    upsert_meeting,
)
from src.extract_actions import create_mock_action_items, validate_action_items
from src.ingest import load_transcript, transcript_to_utterances
from src.preprocess import preprocess_utterances, create_chunks


TRANSCRIPT_PATH = "data/raw/ko_meeting_3speakers.json"


def main():
    data = load_transcript(TRANSCRIPT_PATH)

    utterances = transcript_to_utterances(data)
    utterances = preprocess_utterances(utterances)
    utterances, chunks = create_chunks(utterances)

    action_items = create_mock_action_items()
    action_items = validate_action_items(action_items)
    print("액션아이템 스키마 검증 완료")

    conn = get_connection()
    create_tables(conn)
    upsert_meeting(conn, data)
    save_utterances(conn, utterances)
    save_chunks(conn, chunks)
    save_action_items(conn, action_items)
    conn.close()

    save_slack_payload(action_items, "outputs/slack_payload_sample.json")
    
    print("파이프라인 실행 완료")
    print(f"저장된 발화 수: {len(utterances)}")
    print(f"저장된 청크 수: {len(chunks)}")
    print(f"저장된 액션아이템 수: {len(action_items)}")
    print("Slack payload 저장 완료: outputs/slack_payload_sample.json")


if __name__ == "__main__":
    main()
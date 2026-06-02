from typing import Literal

from pydantic import BaseModel, Field


class ActionItem(BaseModel):
    action_id: str
    meeting_id: str
    owner: str
    owner_role: str
    task: str = Field(min_length=5)
    due_date: str | None = None
    status: Literal["todo", "in_progress", "done", "needs_review"]
    priority: Literal["high", "medium", "low"]
    confidence: float = Field(ge=0.0, le=1.0)
    source_utterance_ids: str
    reason: str = Field(min_length=5)
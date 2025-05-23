from typing import Optional

from pydantic import BaseModel


class PullRequest(BaseModel):
    id: int
    number: int
    title: str
    state: str
    locked: bool
    html_url: str
    body: str
    created_at: str
    updated_at: Optional[str] = None
    closed_at: Optional[str] = None
    merged_at: Optional[str] = None
    user: dict
    base: dict
    head: dict

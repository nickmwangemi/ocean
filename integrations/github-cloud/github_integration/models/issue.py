from pydantic import BaseModel


class Issue(BaseModel):
    id: int
    number: int
    title: str
    state: str
    locked: bool
    html_url: str
    body: str
    created_at: str
    updated_at: str
    closed_at: str
    user: dict

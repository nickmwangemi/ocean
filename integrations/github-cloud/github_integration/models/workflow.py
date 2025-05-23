from pydantic import BaseModel


class Workflow(BaseModel):
    id: int
    name: str
    path: str
    state: str
    created_at: str
    updated_at: str
    url: str
    html_url: str
    badge_url: str

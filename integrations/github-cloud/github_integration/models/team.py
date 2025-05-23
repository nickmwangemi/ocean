from pydantic import BaseModel


class Team(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    privacy: str
    url: str
    members_url: str
    repositories_url: str

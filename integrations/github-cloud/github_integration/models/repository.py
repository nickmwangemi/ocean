from pydantic import BaseModel


class Repository(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    html_url: str
    description: str
    fork: bool
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    homepage: str
    size: int
    stargazers_count: int
    watchers_count: int
    language: str
    forks_count: int
    open_issues_count: int
    default_branch: str

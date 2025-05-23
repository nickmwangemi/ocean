from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class GitHubUser(BaseModel):
    id: int
    login: str
    avatar_url: str
    gravatar_id: Optional[str] = None
    url: str
    html_url: str
    type: str
    site_admin: bool
    name: Optional[str] = None
    company: Optional[str] = None
    blog: Optional[str] = None
    location: Optional[str] = None
    email: Optional[str] = None
    hireable: Optional[bool] = None
    bio: Optional[str] = None
    twitter_username: Optional[str] = None
    public_repos: Optional[int] = None
    public_gists: Optional[int] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True


class GitHubRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: GitHubUser
    html_url: str
    description: Optional[str] = None
    fork: bool
    url: str
    created_at: datetime
    updated_at: datetime
    pushed_at: Optional[datetime] = None
    git_url: str
    ssh_url: str
    clone_url: str
    svn_url: str
    homepage: Optional[str] = None
    size: int
    stargazers_count: int
    watchers_count: int
    language: Optional[str] = None
    has_issues: bool
    has_projects: bool
    has_wiki: bool
    has_pages: bool
    has_downloads: bool
    archived: bool
    disabled: bool
    open_issues_count: int
    license: Optional[Dict[str, Any]] = None
    allow_forking: bool
    is_template: bool
    topics: List[str] = Field(default_factory=list)
    visibility: str
    forks: int
    open_issues: int
    watchers: int
    default_branch: str
    permissions: Optional[Dict[str, bool]] = None

    class Config:
        allow_population_by_field_name = True


class GitHubIssue(BaseModel):
    id: int
    node_id: str
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    number: int
    state: str
    title: str
    body: Optional[str] = None
    user: GitHubUser
    labels: List[Dict[str, Any]] = Field(default_factory=list)
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = Field(default_factory=list)
    milestone: Optional[Dict[str, Any]] = None
    locked: bool
    active_lock_reason: Optional[str] = None
    comments: int
    pull_request: Optional[Dict[str, str]] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    author_association: str
    state_reason: Optional[str] = None

    class Config:
        allow_population_by_field_name = True


class GitHubPullRequest(BaseModel):
    id: int
    node_id: str
    url: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    commits_url: str
    review_comments_url: str
    review_comment_url: str
    comments_url: str
    statuses_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubUser
    body: Optional[str] = None
    labels: List[Dict[str, Any]] = Field(default_factory=list)
    milestone: Optional[Dict[str, Any]] = None
    active_lock_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    closed_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None
    merge_commit_sha: Optional[str] = None
    assignee: Optional[GitHubUser] = None
    assignees: List[GitHubUser] = Field(default_factory=list)
    requested_reviewers: List[GitHubUser] = Field(default_factory=list)
    requested_teams: List[Dict[str, Any]] = Field(default_factory=list)
    head: Dict[str, Any]
    base: Dict[str, Any]
    merged: bool
    mergeable: Optional[bool] = None
    rebaseable: Optional[bool] = None
    mergeable_state: str
    merged_by: Optional[GitHubUser] = None
    comments: int
    review_comments: int
    maintainer_can_modify: bool
    commits: int
    additions: int
    deletions: int
    changed_files: int
    draft: bool

    class Config:
        allow_population_by_field_name = True


class GitHubWorkflow(BaseModel):
    id: int
    node_id: str
    name: str
    path: str
    state: str
    created_at: datetime
    updated_at: datetime
    url: str
    html_url: str
    badge_url: str

    class Config:
        allow_population_by_field_name = True


class GitHubWorkflowRun(BaseModel):
    id: int
    name: Optional[str] = None
    node_id: str
    head_branch: str
    head_sha: str
    path: str
    display_title: str
    run_number: int
    event: str
    status: str
    conclusion: Optional[str] = None
    workflow_id: int
    check_suite_id: int
    check_suite_node_id: str
    url: str
    html_url: str
    pull_requests: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    actor: GitHubUser
    run_attempt: int
    referenced_workflows: List[Dict[str, Any]] = Field(default_factory=list)
    run_started_at: datetime
    triggering_actor: GitHubUser
    jobs_url: str
    logs_url: str
    check_suite_url: str
    artifacts_url: str
    cancel_url: str
    rerun_url: str
    previous_attempt_url: Optional[str] = None
    workflow_url: str
    head_commit: Dict[str, Any]
    repository: GitHubRepository
    head_repository: GitHubRepository

    class Config:
        allow_population_by_field_name = True

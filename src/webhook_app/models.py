# src/webhook_app/models.py
from pydantic import BaseModel
from typing import List, Optional

class FunctionDoc(BaseModel):
    symbol: str                 # fully qualified (e.g., module.Class.method)
    kind: str                   # "function" | "method" | "class"
    status: str                 # "new" | "modified"
    signature: Optional[str]
    summary: str
    params: Optional[str] = None
    returns: Optional[str] = None
    raises: Optional[str] = None
    examples: Optional[str] = None

class FileDoc(BaseModel):
    repo: str
    pr_number: int
    commit_sha: str
    path: str
    language: Optional[str]
    change_type: str            # "added" | "modified"
    high_level_summary: str
    functions: List[FunctionDoc]

class UpsertDoc(BaseModel):
    id: str
    content: str
    repo: str
    path: str
    symbol: Optional[str]
    language: Optional[str]
    pr_number: int
    commit_sha: str
    url: Optional[str]
    kind: str                   # "file_summary" | "function_doc"

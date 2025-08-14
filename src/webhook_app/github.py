# src/webhook_app/github.py
import httpx
from typing import Dict, Any

class GitHub:
    def __init__(self, token: str):
        self._h = {"Authorization": f"token {token}", "Accept":"application/vnd.github+json"}

    async def get_pr_files(self, repo: str, pr: int):
        url = f"https://api.github.com/repos/{repo}/pulls/{pr}/files?per_page=100"
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url, headers=self._h); r.raise_for_status()
            return r.json()

    async def get_file_at_ref(self, repo: str, path: str, ref: str):
        url = f"https://api.github.com/repos/{repo}/contents/{path}?ref={ref}"
        async with httpx.AsyncClient(timeout=30) as c:
            r = await c.get(url, headers=self._h); r.raise_for_status()
            j = r.json()
            if j.get("encoding") == "base64":
                import base64
                return base64.b64decode(j["content"]).decode("utf-8", errors="ignore")
            return ""

# src/webhook_app/main.py
import json
from fastapi import FastAPI, Request, Header, HTTPException
from .security import verify_signature
from .config import Cfg
from .github import GitHub
from .llm_docs import generate_file_doc, flatten_for_upsert
from .embeddings import upsert_docs
from .search import ensure_index

app = FastAPI()

@app.on_event("startup")
def _startup():
    ensure_index()

@app.post("/github/webhook")
async def github_webhook(request: Request, x_hub_signature_256: str | None = Header(None), x_github_event: str | None = Header(None)):
    body = await request.body()
    verify_signature(body, x_hub_signature_256)
    payload = json.loads(body.decode("utf-8"))
    if x_github_event != "pull_request":
        return {"ok": True, "ignored": x_github_event}

    pr = payload["pull_request"]
    action = payload.get("action")
    merged = pr.get("merged", False)
    repo_full = payload["repository"]["full_name"]

    if Cfg.ALLOWED_REPOS and repo_full not in Cfg.ALLOWED_REPOS:
        return {"ok": True, "ignored_repo": repo_full}

    if not (action == "closed" and merged):
        return {"ok": True, "ignored_state": action}

    pr_number = pr["number"]
    commit_sha = pr["merge_commit_sha"]

    gh = GitHub(Cfg.GH_TOKEN)
    files = await gh.get_pr_files(repo_full, pr_number)

    upserts = []
    for f in files:
        if f["status"] not in ["added","modified"]:
            continue
        path = f["filename"]
        language = f.get("patch") and (path.split(".")[-1] if "." in path else None)
        diff = f.get("patch","")
        old_ref = pr["base"]["sha"]
        new_ref = pr["head"]["sha"]

        old = ""
        try:
            if f["status"] == "modified":
                old = await gh.get_file_at_ref(repo_full, path, old_ref)
        except Exception:
            old = ""
        new = await gh.get_file_at_ref(repo_full, path, new_ref)

        file_doc = await generate_file_doc(
            repo=repo_full, pr=pr_number, commit=commit_sha, path=path, language=language,
            diff=diff or "", old=old or "", new=new or ""
        )
        upserts += flatten_for_upsert(file_doc)

    if upserts:
        await upsert_docs(upserts)

    return {"ok": True, "processed_files": len(upserts)}

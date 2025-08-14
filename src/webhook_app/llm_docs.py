from typing import List, Optional
from .config import Cfg
from .models import FileDoc, FunctionDoc, UpsertDoc
from .py_ast import extract_python_symbols, ChangedSymbol
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url=f"{Cfg.AZ_OAI_ENDPOINT}openai/deployments/",
    api_key=Cfg.AZ_OAI_KEY,
)

DOC_SYS_PROMPT = """You are a senior Python engineer generating precise, factual documentation
for source code changes. Your primary signals are the AST-extracted symbols and the
new/old source blocks shown. In your output:
- Do not speculate beyond code.
- Keep summaries 1-3 sentences.
- Prefer bullet points for params/returns/raises.
- If a field is unknown, write "unknown".
- Output only valid JSON per the schema.
"""

DOC_USER_TMPL = """Repo: {repo}
PR: #{pr_number}
File: {path}
Language: python
Commit: {commit_sha}

Changed symbols (Python):
{changed_list}

For each changed symbol below, we give OLD and NEW code blocks.
Use them to produce: a high_level_summary for the file and function-level docs.

{symbol_blocks}

Return JSON: {{"high_level_summary": "...", "functions":[{{"symbol":"...","kind":"function|method|class","status":"new|modified","signature":"...","summary":"...","params":"...","returns":"...","raises":"...","examples":"..."}}]}}
"""

async def generate_file_doc(repo: str, pr: int, commit: str, path: str, language: Optional[str], diff: str, old: str, new: str) -> FileDoc:
    # AST focus on changed Python symbols. Fallback to full-file if parsing fails.
    changed: List[ChangedSymbol] = []
    try:
        changed = extract_python_symbols(old or "", new or "", diff or "")
    except Exception:
        changed = []

    if not changed:
        changed_list = "- (fallback) full-file analysis"
        blocks = f"OLD (truncated):\n```python\n{(old or '')[:2000]}\n```\nNEW (truncated):\n```python\n{(new or '')[:4000]}\n```"
    else:
        changed_list = "\n".join([f"- {c.status.upper()} {c.kind}: {c.symbol} (lines {c.new_start}-{c.new_end})" for c in changed])
        parts = []
        for c in changed:
            parts.append(
                "\n".join([
                    f"# Symbol: {c.symbol}",
                    f"# Kind: {c.kind}",
                    f"# Status: {c.status}",
                    "OLD:\n```python\n" + (c.old_src or "")[:2000] + "\n```",
                    "NEW:\n```python\n" + (c.new_src or "")[:3000] + "\n```",
                ])
            )
        blocks = "\n\n".join(parts)

    user = DOC_USER_TMPL.format(
        repo=repo, pr_number=pr, path=path, commit_sha=commit,
        changed_list=changed_list, symbol_blocks=blocks
    )

    res = await client.chat.completions.create(
        model=Cfg.AZ_OAI_CHAT,
        messages=[{"role":"system","content":DOC_SYS_PROMPT},{"role":"user","content":user}],
        temperature=0.1,
        response_format={"type":"json_object"},
    )
    j = res.choices[0].message.content
    import json
    data = json.loads(j)
    fns = [FunctionDoc(**fd) for fd in data.get("functions", [])]
    return FileDoc(
        repo=repo, pr_number=pr, commit_sha=commit, path=path, language="py",
        change_type="modified", high_level_summary=data.get("high_level_summary", ""), functions=fns
    )

def flatten_for_upsert(fd: FileDoc) -> List[UpsertDoc]:
    docs: List[UpsertDoc] = []
    docs.append(UpsertDoc(
        id=f"{fd.repo}:{fd.commit_sha}:{fd.path}:summary",
        content=f"[FILE SUMMARY]\n{fd.high_level_summary}",
        repo=fd.repo, path=fd.path, symbol=None, language=fd.language,
        pr_number=fd.pr_number, commit_sha=fd.commit_sha,
        url=None, kind="file_summary"
    ))
    for f in fd.functions:
        content_parts = [
            f"[{f.status.upper()} {f.kind.upper()}] {f.symbol}",
            f"Signature: {f.signature or 'unknown'}",
            f"Summary: {f.summary}",
            f"Parameters: {f.params or 'none'}",
            f"Returns: {f.returns or 'none'}",
            f"Raises: {f.raises or 'none'}",
            f"Examples:\n{f.examples or 'n/a'}"
        ]
        docs.append(UpsertDoc(
            id=f"{fd.repo}:{fd.commit_sha}:{fd.path}:{(f.symbol or 'unknown')}",
            content="\n".join(content_parts),
            repo=fd.repo, path=fd.path, symbol=f.symbol, language=fd.language,
            pr_number=fd.pr_number, commit_sha=fd.commit_sha,
            url=None, kind="function_doc"
        ))
    return docs

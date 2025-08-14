# src/rag_service/app.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import AsyncOpenAI
from .config import Cfg
from .retriever import retrieve
from .prompts import SYS, USER_TMPL

client = AsyncOpenAI(
    base_url=f"{Cfg.AZ_OAI_ENDPOINT}openai/deployments/",
    api_key=Cfg.AZ_OAI_KEY,
)

app = FastAPI()

class ChatReq(BaseModel):
    question: str
    k: int = 6

@app.post("/chat")
async def chat(req: ChatReq):
    hits = retrieve(req.question, k=req.k)
    ctx_lines = []
    for h in hits:
        anchor = f"{h['repo']}/{h['path']}#{h.get('symbol') or h['id'].split(':')[-1]}"
        ctx_lines.append(f"[{anchor}] {h['content'][:800]}")
    user = USER_TMPL.format(q=req.question, ctx="\n\n".join(ctx_lines))
    res = await client.chat.completions.create(
        model=Cfg.AZ_OAI_CHAT,
        messages=[{"role":"system","content":SYS},{"role":"user","content":user}],
        temperature=0.2
    )
    return {"answer": res.choices[0].message.content, "citations": [h["id"] for h in hits]}

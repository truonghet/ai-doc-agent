from typing import List
from openai import AsyncOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from .config import Cfg
from .models import UpsertDoc

client = AsyncOpenAI(
    base_url=f"{Cfg.AZ_OAI_ENDPOINT}openai/deployments/",
    api_key=Cfg.AZ_OAI_KEY,
)

search = SearchClient(
    endpoint=Cfg.SEARCH_ENDPOINT,
    index_name=Cfg.SEARCH_INDEX,
    credential=AzureKeyCredential(Cfg.SEARCH_KEY),
)

async def embed_texts(texts: List[str]) -> List[List[float]]:
    res = await client.embeddings.create(
        model=Cfg.AZ_OAI_EMBED,
        input=texts
    )
    return [d.embedding for d in res.data]

async def upsert_docs(docs: List[UpsertDoc]):
    vecs = await embed_texts([d.content for d in docs])
    actions = []
    for d, v in zip(docs, vecs):
        actions.append({
            "@search.action": "mergeOrUpload",
            "id": d.id,
            "content": d.content,
            "repo": d.repo,
            "path": d.path,
            "symbol": d.symbol,
            "language": d.language,
            "pr_number": d.pr_number,
            "commit_sha": d.commit_sha,
            "kind": d.kind,
            "vector": v
        })
    search.upload_documents(actions)

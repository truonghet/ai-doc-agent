# src/rag_service/retriever.py
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from .config import Cfg

client = SearchClient(
    endpoint=Cfg.SEARCH_ENDPOINT,
    index_name=Cfg.SEARCH_INDEX,
    credential=AzureKeyCredential(Cfg.SEARCH_KEY),
)

def retrieve(query: str, k: int = 8, filters: dict | None = None):
    # Simple hybrid: keyword + vector (semantic disabled for brevity)
    results = client.search(
        search_text=query,
        top=k,
        vector={"value": None, "fields": "vector", "k": k},  # Azure will use text query only if no vector; fine for demo
        select=["id","content","repo","path","symbol","pr_number","commit_sha","kind"]
    )
    hits = []
    for r in results:
        hits.append(dict(r))
    return hits

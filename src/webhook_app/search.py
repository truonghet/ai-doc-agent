from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, VectorSearch,
    VectorSearchAlgorithmConfiguration, HnswParameters,
    HnswAlgorithmConfiguration, SearchFieldDataType, SearchField, VectorSearchProfile
)
from azure.core.credentials import AzureKeyCredential
from .config import Cfg

def ensure_index():
    client = SearchIndexClient(Cfg.SEARCH_ENDPOINT, AzureKeyCredential(Cfg.SEARCH_KEY))
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="repo", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="path", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="symbol", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="language", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="pr_number", type=SearchFieldDataType.Int32, filterable=True),
        SimpleField(name="commit_sha", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="kind", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            dimensions=3072,                   # text-embedding-3-large
            vector_search_dimensions=3072,
            vector_search_profile_name="vprof"
        )
    ]
    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="hnsw", parameters=HnswParameters())],
        profiles=[VectorSearchProfile(name="vprof", algorithm_configuration_name="hnsw")]
    )
    index = SearchIndex(name=Cfg.SEARCH_INDEX, fields=fields, vector_search=vector_search)
    try:
        client.create_index(index)
    except Exception:
        # Exists → ignore
        pass

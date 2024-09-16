from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from core.config import settings

# Initialize Elasticsearch connection
async def init_elastic() -> AsyncElasticsearch:
    elastic = AsyncElasticsearch(hosts=[settings.elastic_dsn])
    return elastic

# Dependency for getting Elasticsearch connection
async def get_elastic(elastic: AsyncElasticsearch = Depends(init_elastic)) -> AsyncElasticsearch:
    return elastic

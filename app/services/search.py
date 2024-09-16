import logging
from elasticsearch import AsyncElasticsearch, NotFoundError

logger = logging.getLogger(__name__)

class SearchService:
    async def search(self, query: dict, index: str):
        raise NotImplementedError()


class ElasticSearchService(SearchService):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def search(self, query: dict, index: str):
        try:
            result = await self.elastic.search(index=index, body=query)
            return result["hits"]["hits"]
        except NotFoundError:
            logger.error(f"Search for index {index} and query {query} returned no results")
            return None

    async def get_by_id(self, index: str, object_id: str):
        try:
            result = await self.elastic.get(index=index, id=object_id)
            return result["_source"]
        except NotFoundError:
            logger.error(f"Object with ID {object_id} not found in index {index}")
            return None

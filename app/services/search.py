import logging
from abc import ABC, abstractmethod
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError

logger = logging.getLogger(__name__)


class AsyncSearchEngine(ABC):

    @abstractmethod
    async def get_by_id(self, index: str, _id: str) -> Any | None:
        pass

    @abstractmethod
    async def get_by_ids(self, index: str, ids: list[str]) -> list[Any] | None:
        pass

    @abstractmethod
    async def search(
        self, index: str, query: dict, from_: int, size: int, sort: list[dict] = None
    ) -> list[Any]:
        pass


class ElasticAsyncSearchEngine(AsyncSearchEngine):
    def __init__(self, elastic: AsyncElasticsearch):
        self.elastic = elastic

    async def get_by_id(self, index: str, _id: str) -> Any | None:
        try:
            doc = await self.elastic.get(index=index, id=_id)
            return doc["_source"]
        except NotFoundError:
            return None

    async def get_by_ids(self, index: str, ids: list[str]) -> list[Any] | None:
        docs = []
        for _id in ids:
            doc = await self.get_by_id(index, _id)
            if doc:
                docs.append(doc)
        return docs

    async def search(
        self,
        index: str,
        query: dict,
        from_: int = None,
        size: int = None,
        sort: list[dict] = None,
    ) -> list[Any]:
        try:
            results = await self.elastic.search(
                index=index, from_=from_, size=size, query=query, sort=sort
            )
            return [hit["_source"] for hit in results["hits"]["hits"]]
        except NotFoundError:
            return []


class BaseSearch:
    def __init__(self, search_engine: AsyncSearchEngine):
        self.search_engine = search_engine

    async def get_by_id(self, index: str, obj_id: str) -> Any | None:
        obj = await self.search_engine.get_by_id(index, obj_id)
        return obj

    async def get_by_ids(self, index: str, obj_ids: list[str]) -> list[Any]:
        objs = await self.search_engine.get_by_ids(index, obj_ids)
        return objs

    async def search(
        self,
        index: str,
        query: str,
        from_: int = None,
        size: int = None,
        sort: list[dict] = None,
    ) -> list[Any]:
        results = await self.search_engine.search(index, query, from_, size, sort)
        return results

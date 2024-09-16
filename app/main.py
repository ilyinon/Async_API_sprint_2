from api.v1 import films, genres, persons
from core.config import settings
from db.elastic import init_elastic
from db.redis import init_redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

app = FastAPI(
    title=settings.project_name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)

@app.on_event("startup")
async def startup():
    # Initialize Redis and Elasticsearch connections on startup
    app.state.redis = await init_redis()
    app.state.elastic = await init_elastic()

@app.on_event("shutdown")
async def shutdown():
    # Gracefully close connections on shutdown
    await app.state.redis.close()
    await app.state.elastic.close()


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

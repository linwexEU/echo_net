from fastapi import FastAPI 
from src.api.routers import all_routers
from src.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from contextlib import asynccontextmanager
import logging 
import src.logger


logger = logging.getLogger(__name__)


@asynccontextmanager 
async def lifespan(app: FastAPI): 
    redis = aioredis.from_url(settings.REDIS_URL) 
    FastAPICache.init(RedisBackend(redis), prefix="redis-cache")
    logger.info("Redis connected!")
    yield 
    logger.info("Redis disconnected!")


app = FastAPI(lifespan=lifespan) 

for router in all_routers: 
    app.include_router(router) 

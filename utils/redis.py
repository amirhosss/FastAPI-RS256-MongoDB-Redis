import aioredis

from core.config import settings

redis = aioredis.Redis(
    host=settings.REDIS_URL,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True
)
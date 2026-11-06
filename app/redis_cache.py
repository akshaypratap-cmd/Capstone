import json
import logging
from typing import Any

import redis

from app.config import settings


logger = logging.getLogger(__name__)


# Create Redis client
# Redis operations will attempt to reconnect when necessary
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=2,
    health_check_interval=30
)


# Get cached data
def get_cache(key: str) -> Any | None:

    try:

        data = redis_client.get(key)

        if data is None:
            return None

        try:
            return json.loads(data)

        except json.JSONDecodeError:

            logger.warning(
                "Invalid JSON found in Redis cache for key: %s",
                key
            )

            delete_cache(key)

            return None

    except redis.RedisError:

        logger.exception("Redis cache read failed")

        return None


# Save data in cache
def set_cache(
    key: str,
    data: Any,
    expire: int = 60
) -> None:

    if expire <= 0:

        logger.warning("Cache expiration must be greater than zero")

        return

    try:

        redis_client.set(
            key,
            json.dumps(data),
            ex=expire
        )

    except (redis.RedisError, TypeError, ValueError):

        logger.exception("Redis cache write failed")


# Delete cached data
def delete_cache(key: str) -> None:

    try:

        redis_client.delete(key)

    except redis.RedisError:

        logger.exception("Redis cache deletion failed")
import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)

def get_cached_key(product_id: int) -> str:
    return f"product:{product_id}"

def cache_get(key: str):
    raw = redis_client.get(key)
    if raw is None:
        return None
    return json.loads(raw)

def cache_set(key: str, value: dict, ttl_seconds: int):
    redis_client.set(key, json.dumps(value), ex=ttl_seconds)

def cache_delete(key: str):
    redis_client.delete(key)
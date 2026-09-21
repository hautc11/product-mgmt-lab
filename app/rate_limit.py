from fastapi import Request

from app import cache
from app.errors import RateLimitExceededError


def rate_limiter(max_requests: int, window_seconds: int):
    def dependency(request: Request):
        client_ip = request.client.host
        key = f"ratelimit:{client_ip}:{request.url.path}"

        current = cache.redis_client.incr(key)
        if current == 1:
            cache.redis_client.expire(key, window_seconds)

        if current > max_requests:
            retry_after = cache.redis_client.ttl(key)
            raise RateLimitExceededError(retry_after=max(retry_after, 1))

    return dependency
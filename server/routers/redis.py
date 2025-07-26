"""
Redis router for handling Redis operations.
"""

import redis
from fastapi import APIRouter, HTTPException
from core.config import get_redis_url

router = APIRouter()

@router.get("/ping")
async def ping_redis():
    """Test Redis connectivity."""
    try:
        r = redis.Redis.from_url(get_redis_url())
        r.ping()
        return {"status": "Redis is connected", "url": get_redis_url()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {str(e)}")

@router.post("/set")
async def set_redis_value(key: str, value: str):
    """Test Redis set operation."""
    try:
        r = redis.Redis.from_url(get_redis_url())
        r.set(key, value)
        return {"status": "success", "key": key, "value": value}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis set operation failed: {str(e)}")

@router.get("/get/{key}")
async def get_redis_value(key: str):
    """Test Redis get operation."""
    try:
        r = redis.Redis.from_url(get_redis_url())
        value = r.get(key)
        return {"status": "success", "key": key, "value": value.decode() if value else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis get operation failed: {str(e)}")
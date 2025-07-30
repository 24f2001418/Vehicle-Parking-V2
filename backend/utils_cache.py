# utils_cache.py
# Redis caching and rate-limiting decorators for Flask APIs
import redis
import functools
import hashlib
import time
from flask import request, jsonify, g

REDIS_URL = 'redis://localhost:6379/0'
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

def make_cache_key(prefix, timeout=60):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            key_base = f"{prefix}:{request.path}:{request.query_string.decode()}"
            key = hashlib.sha256(key_base.encode()).hexdigest()
            cached = redis_client.get(key)
            if cached:
                return jsonify(eval(cached))
            resp = fn(*args, **kwargs)
            # Only cache successful responses
            if hasattr(resp, 'status_code') and resp.status_code == 200:
                redis_client.setex(key, timeout, str(resp.get_json()))
            return resp
        return wrapper
    return decorator

def rate_limit(limit=10, period=60):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or 'global'
            key = f"rl:{fn.__name__}:{ip}"
            now = int(time.time())
            window = now // period
            rl_key = f"{key}:{window}"
            count = redis_client.incr(rl_key)
            if count == 1:
                redis_client.expire(rl_key, period)
            if count > limit:
                return jsonify({'msg': 'Rate limit exceeded. Try again later.'}), 429
            return fn(*args, **kwargs)
        return wrapper
    return decorator

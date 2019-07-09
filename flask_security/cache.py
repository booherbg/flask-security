# -*- coding: utf-8 -*-
"""
    flask_security.cache
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Flask-Security token cache module

    :copyright: (c) 2019.
    :license: MIT, see LICENSE for more details.
"""

from cachetools import TTLCache

from .utils import config_value


class VerifyHashCache:
    """Cache handler to make it quick password check by bypassing
    already checked passwords against exact same couple of token/password.
    This cache handler is more efficient on small apps that
    run on few processes as cache is only shared between threads.
    """

    def __init__(self):
        ttl = config_value("VERIFY_HASH_CACHE_TTL", default=(60 * 5))
        max_size = config_value("VERIFY_HASH_CACHE_MAX_SIZE", default=500)
        self._cache = TTLCache(max_size, ttl)

    def has_verify_hash_cache(self, user):
        """Check given user id is in cache."""
        return self._cache.get(user.id)

    def set_cache(self, user):
        """When a password is checked, then result is put in cache."""
        self._cache[user.id] = True

    def clear(self):
        """Clear cache"""
        self._cache.clear()

class VerifyHashCacheRedis:
    """Cache handler to make it quick password check by bypassing
    already checked passwords against exact same couple of token/password.
    
    This Cache supports redis
    """

    def __init__(self):
        #self.use_redis = config_value("VERIFY_HASH_USE_REDIS", default=False)
        print('Using Redis!')
        import redis
        self.ttl = config_value("VERIFY_HASH_CACHE_TTL", default=(60 * 5))
        redis_server = config_value("VERIFY_HASH_REDIS_SERVER", default='localhost')
        redis_password = config_value("VERIFY_HASH_REDIS_PASSWORD", default=None)
        redis_port = config_value("VERIFY_HASH_REDIS_PORT", default=6379)
        redis_db = config_value("VERIFY_HASH_REDIS_DB", default=1)
        self._cache = redis.Redis(host=redis_server, port=redis_port, db=redis_db, password=redis_password)
        assert self._cache.ping()

    def has_verify_hash_cache(self, user):
        """Check given user id is in cache."""
        hit = self._cache.get('user-%d' % user.id) is not None
        print(hit)
        return hit

    def set_cache(self, user):
        """When a password is checked, then result is put in cache."""
        self._cache.set('user-%d' % user.id, '1', ex=self.ttl)

    def clear(self):
        """Clear cache"""
        self._cache.flushdb()
import random
import functools
import logging
import pickle
from inspect import iscoroutinefunction

import redis
from binascii import crc32
from tornado.ioloop import IOLoop
from tornado.options import options
from .exception import PermissionDenied


redis_pool = redis.ConnectionPool(
    host=options.REDIS_HOST,
    port=options.REDIS_PORT,
    db=options.REDIS_DB
)


def redis_cli():
    return redis.StrictRedis(
        connection_pool=redis_pool,
        decode_responses=True,  # 自动解码
    )


def gen_prefix(obj, method):
    return '.'.join([obj.__module__, obj.__class__.__name__, method.__name__])


def get_name(self, method, args, kwargs, key=None, prefix=None, attr_key=None, attr_prefix=None, namespace=options.REDIS_NAMESPACE):
    name = key or kwargs.get('key', None) or (attr_key and getattr(self, attr_key))
    if not name:
        _prefix = prefix or (attr_prefix and getattr(self, attr_prefix)) or gen_prefix(self, method)
        name = "%s:%u" % (_prefix, crc32(pickle.dumps(args) + pickle.dumps(kwargs)))
    name = namespace and "{}:{}".format(namespace, name) or name
    return name


def lock(key=None, prefix=None, attr_key=None, attr_prefix=None, timeout=60, namespace=options.REDIS_NAMESPACE):
    def decorate(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            name = get_name(self, method, args, kwargs, key=key, prefix=prefix, attr_key=attr_key, attr_prefix=attr_prefix, namespace=namespace)
            redis_lock = redis.lock.Lock(redis_cli(), name, timeout=timeout)
            if redis_lock.acquire(blocking=False):
                try:
                    res = method(self, *args, **kwargs)
                    return res
                finally:
                    try:
                        redis_lock.release()
                    except Exception as e:
                        logging.exception(e)
            else:
                raise PermissionDenied('任务忙，请稍后再试')

        @functools.wraps(method)
        async def async_wrapper(self, *args, **kwargs):
            name = get_name(self, method, args, kwargs, key=key, prefix=prefix, attr_key=attr_key, attr_prefix=attr_prefix, namespace=namespace)
            redis_lock = redis.lock.Lock(redis_cli(), name, timeout=timeout)
            if redis_lock.acquire(blocking=False):
                try:
                    res = await method(self, *args, **kwargs)
                    return res
                finally:
                    try:
                        redis_lock.release()
                    except Exception as e:
                        logging.exception(e)
            else:
                raise PermissionDenied('任务忙，请稍后再试')

        return async_wrapper if iscoroutinefunction(method) else wrapper
    return decorate


def stalecache(key=None, prefix=None, attr_key=None, attr_prefix=None, namespace=options.REDIS_NAMESPACE,
               expire=600, stale=3600, time_lock=1, time_delay=1, max_time_delay=10):
    def decorate(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            name = get_name(self, method, args, kwargs, key=key, prefix=prefix, attr_key=attr_key, attr_prefix=attr_prefix, namespace=namespace)
            res = redis_cli().pipeline().ttl(name).get(name).execute()
            v = pickle.loads(res[1]) if res[0] > 0 and res[1] else None
            if res[0] <= 0 or res[0] < stale:

                def func():
                    value = method(self, *args, **kwargs)
                    logging.debug("update cache: %s", name)
                    redis_cli().pipeline().set(
                        name, pickle.dumps(value)
                    ).expire(name, expire + stale).execute()
                    return value

                # create new cache in blocking modal, if cache not exists.
                if res[0] <= 0:
                    return func()

                # create new cache in non blocking modal, and return stale data.
                # set expire to get a "lock", and delay to run the task
                real_time_delay = random.randrange(time_delay, max_time_delay)
                redis_cli().expire(name, stale + real_time_delay + time_lock)
                IOLoop.current().add_timeout(IOLoop.current().time() + real_time_delay, func)

            return v

        @functools.wraps(method)
        async def async_wrapper(self, *args, **kwargs):
            if kwargs.get('skip_cache'):
                return await method(self, *args, **kwargs)

            name = get_name(self, method, args, kwargs, key=key, prefix=prefix, attr_key=attr_key, attr_prefix=attr_prefix, namespace=namespace)
            res = redis_cli().pipeline().ttl(name).get(name).execute()
            v = pickle.loads(res[1]) if res[0] > 0 and res[1] else None
            if res[0] <= 0 or res[0] < stale:

                async def func():
                    value = await method(self, *args, **kwargs)
                    logging.debug("update cache: %s", name)
                    redis_cli().pipeline().set(
                        name, pickle.dumps(value)
                    ).expire(name, expire + stale).execute()
                    return value

                # create new cache in blocking modal, if cache not exists.
                if res[0] <= 0:
                    return await func()

                # create new cache in non blocking modal, and return stale data.
                # set expire to get a "lock", and delay to run the task
                real_time_delay = random.randrange(time_delay, max_time_delay)
                redis_cli().expire(name, stale + real_time_delay + time_lock)
                IOLoop.current().add_timeout(IOLoop.current().time() + real_time_delay, func)

            return v

        return async_wrapper if iscoroutinefunction(method) else wrapper
    return decorate


def delete(key=None, prefix=None, attr_key=None, attr_prefix=None, namespace=options.REDIS_NAMESPACE,
           target=None, stale=3600):
    def decorate(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            value = method(self, *args, **kwargs)
            c = redis_cli()

            # delete by key
            name = key or kwargs.get('key', None) or (attr_key and getattr(self, attr_key))
            if name:
                name = namespace and "{}:{}".format(namespace, name) or name
                c.expire(name, stale)

            # delete by prefix
            _prefix = prefix or (attr_prefix and getattr(self, attr_prefix))\
                or (target and hasattr(self, target) and gen_prefix(self, getattr(self, target)))
            if _prefix:
                _prefix = namespace and "{}:{}".format(namespace, _prefix) or _prefix
                for name in c.keys(pattern="{}*".format(_prefix)):
                    c.expire(name, stale)

            return value
        return wrapper
    return decorate

import functools
from collections import namedtuple
from datetime import datetime, timedelta

TimeLimitCacheInfo = namedtuple('TimeLimitCacheInfo', ['size', 'maxsize', 'hits', 'misses'])


def time_limit_cache(maxsize=32, duration_minutes=None):
    """Lazy cache"""
    if maxsize is not None and not isinstance(maxsize, int):
        raise TypeError('Expected maxsize to be an integer or None')

    def decorated_func(func):
        return _time_cache_wrapper(func, maxsize, duration_minutes, TimeLimitCacheInfo)
    return decorated_func


def _time_cache_wrapper(func, maxsize, duration_minutes, cache_info_creator):
    full = False
    hits = 0
    misses = 0
    not_found = object()
    cache = {}  # key: (create_time, obj)
    cache_get = cache.get
    now = datetime.now
    make_key = functools._make_key
    tdelta = timedelta(minutes=duration_minutes) if duration_minutes else None

    def _del_oldest():
        if cache:
            del cache[sorted(cache.items(), key=lambda x: x[1][0])[0][0]]

    if maxsize == 0:
        def wrapper(*args, **kwargs):
            nonlocal misses
            result = func(*args, **kwargs)
            misses += 1
            return result
    elif maxsize is None:
        def wrapper(*args, **kwargs):
            nonlocal hits, misses
            key = make_key(args, kwargs, False)
            result = cache_get(key, not_found)
            if result is not not_found:
                hits += 1
                return result
            result = func(*args, **kwargs)
            cache[key] = (now(), result)
            misses += 1
            return result
    else:
        def wrapper(*args, **kwargs):
            nonlocal hits, misses, full
            key = make_key(args, kwargs, False)
            obj = cache_get(key, not_found)
            if obj is not not_found:
                created, result = obj
                if tdelta is not None:
                    if (now() - created) < tdelta:
                        hits += 1
                        return result
                    del cache[key]
                else:
                    return result
            result = func(*args, **kwargs)
            if key in cache:
                pass
            elif full:
                _del_oldest()
            else:
                full = (len(cache) >= maxsize)
            cache[key] = (now(), result)
            return result

    def get_info():
        return cache_info_creator(len(cache), maxsize, hits, misses)

    def clear():
        nonlocal hits, misses, full
        cache.clear()
        hits = misses = 0
        full = False

    wrapper.get_info = get_info
    wrapper.clear = clear
    return wrapper

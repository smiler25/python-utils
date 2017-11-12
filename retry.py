import time
import functools
from types import GeneratorType


def retry(retries=1, wait=1, *, until_ok=False, error_cb=None, logger=None):
    """
    Decorator for several retries

    :param retries: number of retries
    :param wait: delay between retires (seconds)
    :param until_ok: retry until function complete without error
    :param error_cb: callable which will be called after every exception
    :param logger: python logger for errors
    """

    if error_cb is not None and not callable(error_cb):
        error_cb = None
        if logger is not None:
            logger.warning('RETRY INIT error_cb is not callable: error_cb={}'
                           .format(error_cb))

    def inner(func):
        if until_ok:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                while True:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        time.sleep(wait)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for i in range(1, retries+1):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if i == retries:
                            if logger is not None:
                                logger.error('RETRY ERROR: func={} module={} error={}'
                                             .format(func.__qualname__, func.__module__, e),
                                             exc_info=True)
                            raise
                        if error_cb is not None:
                            error_cb()
                        time.sleep(wait)
        return wrapper
    return inner


def retry_result(retries=2, wait=0):
    """
    Decorator for several retries to receive result (bool(res))

    :param retries: number of retries
    :param wait: delay between retires (seconds)
    """
    def inner(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(1, retries+1):
                res = func(*args, **kwargs)
                if res:
                    return res
                if i == retries:
                    return
                time.sleep(wait)
        return wrapper
    return inner


def try_iterable(data, func, retries):
    """
    Function for several retries on iterable

    :param data: iterable object (list, tuple, generator)
    :param func: func to call on each element
    :param retries: number of retries
    :returns bool, None or iterable:
            (True, None) if complete all elements
            (False, iterable) if not complete all elements
        if data is generator generator will be returned
        else list with unprocessed elements will be returned
    """

    if isinstance(data, GeneratorType):
        generator = data
    else:
        generator = (o for o in data)
    for _ in range(retries):
        print('retry', _)
        try:
            for one in generator:
                func(one)
            return True, None
        except:
            print('Error')

    if isinstance(data, GeneratorType):
        return False, data
    return False, list(generator)

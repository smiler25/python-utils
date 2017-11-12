import functools
import time


def repeat(*, minutes=None, seconds=None, exit_exc=None, logger=None):
    """
    Repeats decorated function every preset time after its execution
    minutes and seconds can be combined

    :param minutes: number of minutes
    :param seconds: number of seconds
    :param exit_exc: exception(-s) after which the function terminates
    :param logger: python logger for errors
    """
    sleep_time = 0
    if minutes is not None:
        if not isinstance(minutes, int):
            if logger is not None:
                logger.error('REPEAT INIT ERROR: Minutes must be integer or None',
                             exc_info=True)
            raise AttributeError('Minutes must be int or None')
        sleep_time += minutes * 60
    if seconds is not None:
        if not isinstance(seconds, int):
            if logger is not None:
                logger.error('REPEAT INIT ERROR: Seconds must be integer or None',
                             exc_info=True)
            raise AttributeError('Seconds must be int or None')
        sleep_time += seconds

    if exit_exc is not None:
        if isinstance(exit_exc, (list, tuple)):
            for one in exit_exc:
                if not issubclass(one, BaseException):
                    if logger is not None:
                        logger.error('REPEAT INIT ERROR: '
                                     'Exceptions must be subclasses of BaseException',
                                     exc_info=True)
                    raise AttributeError('Exceptions must be subclasses of BaseException')
                exit_exc_list = (KeyboardInterrupt, SystemExit) + tuple(exit_exc)
        elif issubclass(exit_exc, BaseException):
            exit_exc_list = (exit_exc, KeyboardInterrupt, SystemExit)
    else:
        exit_exc_list = (KeyboardInterrupt, SystemExit)

    def decorator(func):
        return _repeat_wrapper(func, sleep_time, exit_exc_list, logger)
    return decorator


def _repeat_wrapper(func, sleep_time, exit_exc=None, logger=None):
    if exit_exc is not None:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except exit_exc as e:
                    if logger is not None:
                        logger.error('REPEAT ERROR: func={} module={} error={}'
                                     .format(func.__qualname__, func.__module__, e),
                                     exc_info=True)
                    raise
                except BaseException as e:
                    if logger is not None:
                        logger.error('REPEAT ERROR: func={} module={} error={}'
                                     .format(func.__qualname__, func.__module__, e),
                                     exc_info=True)
                time.sleep(sleep_time)
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                try:
                    func(*args, **kwargs)
                except BaseException as e:
                    if logger is not None:
                        logger.error('REPEAT ERROR: func={} error={}'.format(func, e),
                                     exc_info=True)
                time.sleep(sleep_time)
    return wrapper

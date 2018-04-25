import time, logging

from django.conf import settings

logger = logging.getLogger(__name__)


def timeit(func):
    def __decorator(*args, **kwags):
        start = time.time()
        result = func(*args, **kwags)  #recevie the native function call result
        span = time.time() - start
        args_strs = [repr(arg) for arg in args] + [k + '=' + repr(w) for k, w in kwags.iteritems()]
        if span > settings.SLOW_RESPONSE_LOG_TIME:
            if not settings.DEBUG and span > settings.SLOW_RESPONSE_WARNING_TIME:
                logging.exception('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
            else:
                logging.warning('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
        return result        #return to caller
    return __decorator

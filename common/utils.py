import time, logging

from django.conf import settings

logger = logging.getLogger(__name__)


def timeit(func):
    def __decorator(*args, **kwags):
        start = time.time()
        result = func(*args, **kwags)  #recevie the native function call result
        span = time.time() - start
        args_strs = [repr(arg) for arg in args] + [k + '=' + repr(w) for k, w in kwags.iteritems()]
        if settings.DEBUG and span > 0.2:
            logging.warning('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
        if not settings.DEBUG and span > 3.0:
            logging.exception('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
        return result        #return to caller
    return __decorator

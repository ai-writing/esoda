import time, logging, requests, json

from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.utils.text import Truncator

logger = logging.getLogger(__name__)


def timeit(func):
    def __decorator(*args, **kwags):
        start = time.time()
        result = func(*args, **kwags)  #recevie the native function call result
        span = time.time() - start
        if span > settings.SLOW_RESPONSE_LOG_TIME:
            args_strs = [Truncator(arg).words(10) for arg in args] + [k + '=' + Truncator(w).words(10) for k, w in kwags.iteritems()]
            if not settings.DEBUG and span > settings.SLOW_RESPONSE_WARNING_TIME:
                logging.exception('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
            else:
                logging.warning('timeit: %s %d ms\n(%s)', func.__name__, span * 1000, ', '.join(args_strs))
        return result        #return to caller
    return __decorator


class AdminSlackHandler(AdminEmailHandler):
    def send_mail(self, subject, message, *args, **kwargs):
        if not settings.SLACK_WEBHOOK_URL:
            return
        data = {
            'attachments': [
                {
                    'color': 'danger',
                    'pretext': subject,
                    'text': message,
                }
            ]
        }
        try:
            requests.post(settings.SLACK_WEBHOOK_URL, {'payload': json.dumps(data)}, timeout=10)
        except Exception as e:
            logger.warning('AdminSlackHandler Error: %s', repr(e))

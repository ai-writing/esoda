import requests, logging

logger = logging.getLogger(__name__)

from django.conf import settings

LEMMATIZER_URL = settings.STANFORD_CORENLP_SERVER + '?properties={"outputFormat":"conll"}'


def lemmatize(s):
    '''
    s: a English string
    return: a list of lower-cased lemmas
    '''

    try:
        conll = requests.post(LEMMATIZER_URL, s, timeout=10).text  # may end with \r\n
        lines = [line.strip() for line in conll.split('\n')]
        tokens = [line.split('\t') for line in lines if line]
        logger.info('conll: "%s" -> %s', s, tokens)
        ll = [t[2].lower() for t in tokens]
        ref = [t[1] for t in tokens]
    except Exception as e:
        logger.exception('Failed to lemmatize "%s"', s)
        ll = ref = s.split()
        ll = [l.lower() for l in ll]

    return ll, ref

lemmatize('checking')

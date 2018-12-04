import xml.dom.minidom
import requests, logging, random, hashlib
from .utils import has_cn
from common.utils import timeit
import heapq
from common.mongodb import MONGODB
import math
import re

from django.conf import settings

logger = logging.getLogger(__name__)
if not settings.DEBUG:
    import requests_cache
    requests_cache.install_cache('youdao_cache', backend='memory', expire_after=86400)


YOUDAO_SUGGEST_URL = 'http://dict.youdao.com/suggest?ver=2.0&le=en&num=10&q=%s'

@timeit
def youdao_suggest(q, timeout=10):
    r = {}
    suggests = []
    try:
        xmlstring = requests.get(YOUDAO_SUGGEST_URL % q, timeout=timeout).text
        DOMTree = xml.dom.minidom.parseString(xmlstring.encode('utf-8')).getElementsByTagName('suggest');
        items = DOMTree[0].getElementsByTagName('item')
        for item in items:
            suggest = {}
            word = item.getElementsByTagName('title')[0].firstChild.wholeText
            desc = item.getElementsByTagName('explain')[0].firstChild.wholeText
            if word.find(' ') < 0:
                suggest['category'] = 'Words'
            else:
                suggest['category'] = 'Expressions'
            suggest['label'] = word
            suggest['desc'] = desc
            suggests.append(suggest)
    except Exception as e:
        logger.exception('Failed in Youdao suggest "%s"', q)
    r['suggest'] = suggests
    logger.info('youdao_suggest: "%s" -> %s', q, repr(suggests))
    return r

def rank(item, len_q):
    mul = 0
    diff = len(item['_id']) - len_q
    if diff == 0:
        mul = 0
    elif diff >= 6:
        mul = 3
    else:
        mul = diff/2 + 1
    # return mul * math.log(item['tf'])
    return mul * item['tf']

@timeit
def suggest_new(q):
    r = {}
    suggests = []
    words = []
    len_q = len(q)
    suggest_num = 10
    collection = MONGODB.common.suggest
    q_conv = re.escape(q)
    q_str = '^' + str(q_conv) + '.*'
    word = collection.find_one({'_id': q_str})
    if word:
        words.append(word)
        suggest_num -= 1
    arr = list(collection.find({'_id': {'$regex': q_str}}).sort([('tf', -1)]).limit(1000))
    words.extend(heapq.nlargest(suggest_num, arr, key=lambda s: rank(s, len_q)))
    for word in words:
        suggest = {}
        if suggests and word['_id'] == q:
            continue
        if word['_id'].find(' ') < 0:
            suggest['category'] = 'Words'
        else:
            suggest['category'] = 'Expressions'
        suggest['label'] = word['_id']
        suggest['desc'] = "; ".join(list(word['meanings']))
        suggests.append(suggest)
    r['suggest'] = suggests
    # logger.info('suggest_new: "%s" -> %s', q, repr(suggests))
    return r

YOUDAO_SEARCH_URL = 'http://dict.youdao.com/jsonapi?dicts={count:1,dicts:[[\"ec\"]]}&q=%s'

def youdao_search(q0, q, timeout=10):
    dictionary = {}
    try:
        jsonObj = requests.get(YOUDAO_SEARCH_URL % q, timeout=timeout).json()
        cn = has_cn(q0)
        q = q0 if cn else q

        if 'simple' in jsonObj and 'ec' in jsonObj:
            dictionary = {
                'word': q,
                'english': jsonObj['simple']['word'][0].get('ukphone', ''),
                'american': jsonObj['simple']['word'][0].get('usphone', ''),
                'explanationList': []
            }
            for explain in jsonObj['ec']['word'][0]['trs']:
                dictionary['explanationList'].append(explain['tr'][0]['l']['i'][0])
    except Exception:
        logger.exception('Failed in Youdao dict search "%s" "%s"', q0, q)
    dictionary['cn'] = cn
    logger.info('youdao_search: "%s", "%s" -> %s', q0, q, repr(dictionary))
    return dictionary

YOUDAO_TRANSLATE_URL = 'http://fanyi.youdao.com/openapi.do?keyfrom=ESLWriter&key=205873295&type=data&doctype=json&version=1.2&q=%s'

@timeit
def youdao_translate_old(q, timeout=10):
    try:
        response = requests.get(YOUDAO_TRANSLATE_URL % q, timeout=timeout)
        r = response.json()
    except Exception:
        logger.exception('Failed in Youdao translate "%s"', q)
        return {}
    basic_explains = r.get('basic', {}).get('explains', [])
    if basic_explains == []:
        explanation_str = r.get('translation', [])[0]
    else:
        explanation_str = basic_explains[0][basic_explains[0].find(']')+1:].strip()
        if has_cn(explanation_str):
            explanation_str = r.get('translation', [])[0]

    translated = {
        # 'explanationList': r.get('basic', {}).get('explains', []) + r.get('translation', []),
        'explanationList': explanation_str,
        'cached': response.from_cache if hasattr(response, 'from_cache') else False
    }
    logger.info('youdao_translate: "%s" -> %s', r.get('query', q), repr(translated))
    return translated

YOUDAO_API_URL = 'http://openapi.youdao.com/api'

def generate_translate_url(q):
    fromLang = 'auto'
    toLang = 'en'
    salt = random.randint(1, 65536)
    sign = settings.YOUDAO_APP_KEY + q + str(salt) + settings.YOUDAO_SECRET_KEY
    m1 = hashlib.md5()
    m1.update(sign.encode('utf-8'))
    sign = m1.hexdigest()
    translate_url = YOUDAO_API_URL + '?appKey=' + settings.YOUDAO_APP_KEY + '&q=' + q + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(salt) + '&sign=' + sign
    return translate_url

@timeit
def youdao_translate_new(q, timeout=10):
    try:
        translate_url = generate_translate_url(q)
        response = requests.get(translate_url, timeout=timeout)
        if response:
            r = response.json()
        else:
            return {}
    except Exception:
        logger.exception('Failed in Youdao translate "%s"', q)
        return {}
    translated = {
        'explanationList': r.get('basic', {}).get('explains', []) + r.get('translation', []),
        'cached': response.from_cache if hasattr(response, 'from_cache') else False
    }
    logger.info('youdao_translate: "%s" -> %s', r.get('query', q), repr(translated))
    return translated

import xml.dom.minidom
import requests, logging
from .utils import has_cn

logger = logging.getLogger(__name__)
# TODO: install requests_cache


YOUDAO_SUGGEST_URL = 'http://dict.youdao.com/suggest?ver=2.0&le=en&num=10&q=%s'

def youdao_suggest(q):
    r = {}
    suggests = []
    try:
        xmlstring = requests.get(YOUDAO_SUGGEST_URL % q, timeout=10).text
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
    return r

YOUDAO_SEARCH_URL = 'http://dict.youdao.com/jsonapi?dicts={count:1,dicts:[[\"ec\"]]}&q=%s'

def youdao_search(q0, q):
    dictionary = {}
    try:
        jsonObj = requests.get(YOUDAO_SEARCH_URL % q, timeout=10).json()
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
    return dictionary

YOUDAO_TRANSLATE_URL = 'http://fanyi.youdao.com/openapi.do?keyfrom=ESLWriter&key=205873295&type=data&doctype=json&version=1.2&q=%s'

def youdao_translate(q):
    r = {}
    try:
        r = requests.get(YOUDAO_TRANSLATE_URL % q, timeout=10).json()
    except Exception:
        logger.exception('Failed in Youdao translate "%s"', q)
    return {
        'query': r.get('query', q),
        'explanationList': r.get('basic', {}).get('explains', []) + r.get('translation', []),
        'cn': has_cn(q)
    }

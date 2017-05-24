import xml.dom.minidom
import requests
import json

YOUDAO_SUGGEST_URL = 'http://dict.youdao.com/suggest?ver=2.0&le=en&num=10&q=%s'

def youdao_suggest(q):
    r = {}
    xmlstring = requests.get(YOUDAO_SUGGEST_URL % q, timeout=10).text
    DOMTree = xml.dom.minidom.parseString(xmlstring.encode('utf-8')).getElementsByTagName('suggest');
    suggests = []
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
    r['suggest'] = suggests
    return r

YOUDAO_SEARCH_URL = 'http://dict.youdao.com/jsonapi?dicts={count:1,dicts:[[\"ec\"]]}&q=%s'

def youdao_search(q):
    jsonString = requests.get(YOUDAO_SEARCH_URL % q, timeout=10).text
    jsonObj = json.loads(jsonString.encode('utf-8'))

    if 'simple' in jsonObj and 'ec' in jsonObj:
        dictionary = {
            'word': q,
            'english': jsonObj['simple']['word'][0].get('ukphone', ''),
            'american': jsonObj['simple']['word'][0].get('usphone', ''),
            'explanationList': []
        }
        for explain in jsonObj['ec']['word'][0]['trs']:
            dictionary['explanationList'].append(explain['tr'][0]['l']['i'][0])
        return dictionary
    return {}
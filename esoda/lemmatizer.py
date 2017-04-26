import requests

STANFORD_CORENLP_SERVER = 'http://166.111.139.15:8004/'
LEMMATIZER_URL = STANFORD_CORENLP_SERVER + '?properties={"outputFormat":"conll"}'

def lemmatize(s):
    '''
    s: a English string
    return: a list of lower-cased lemmas
    '''

    try:
        conll = requests.post(LEMMATIZER_URL, s, timeout=10).text
        ll = [line.split('\t')[2].lower() for line in conll.split('\n') if line]
    except Exception as e:
        print repr(e)
        ll = s.split()

    return ll

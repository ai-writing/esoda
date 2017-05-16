import requests, logging

STANFORD_CORENLP_SERVER = 'http://166.111.139.15:8004/'
LEMMATIZER_URL = STANFORD_CORENLP_SERVER + '?properties={"outputFormat":"conll"}'

def lemmatize(s):
    '''
    s: a English string
    return: a list of lower-cased lemmas
    '''

    try:
        conll = requests.post(LEMMATIZER_URL, s, timeout=10).text
        tokens = [line.split('\t') for line in conll.split('\n') if line]
        ll = [t[2].lower() for t in tokens]
        ref = [t[1] for t in tokens]
    except Exception as e:
        logging.exception('Failed to lemmatize')
        ll = ref = s.split()
        ll = [l.lower() for l in ll]

    return ll, ref

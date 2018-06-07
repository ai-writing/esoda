import requests, logging

logger = logging.getLogger(__name__)

from common.utils import timeit
from django.conf import settings

LEMMATIZER_URL = settings.STANFORD_CORENLP_SERVER + '?properties={"outputFormat":"conll"}'
ESL_DEP_TYPES = ['NSUBJ', 'DOBJ', 'IOBJ', 'NSUBJPASS', 'AMOD', 'NN', 'ADVMOD', 'PARTMOD', 'PREP', 'POBJ', 'PRT',
    'COMPOUND', 'COMPOUND:PRT', 'CASE', 'MWE']
VERB_TYPES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
PREP_TYPES = ['IN', 'TO']
ADV_TYPES = ['RB', 'RBR', 'RBS', 'RP']
ADJ_TYPES = ['JJ', 'JJR', 'JJS']
NOUN_TYPES = ['NN', 'NNP', 'NNPS', 'NNS']

def is_esl_dep(dt, t, td):
    return _is_esl_dep((dt, (None, t['l'], t['pt']), (None, td['l'], td['pt'])))

def convert_dep(dt, t, td):
    dt, t1, t2 = _convert_dep((dt, t, td, (None, t['l'], t['pt']), (None, td['l'], td['pt'])))
    return {'dt': str(dt), 'l1': t1['l'], 'i1': str(t1['i']), 'l2': t2['l'], 'i2': str(t2['i'])}

# format of d:
# (type, token1, token2)
# format of token:
# (None, lemma, pos)
def _is_esl_dep(d):
    if d[0] not in ESL_DEP_TYPES:
        return False
    t1 = d[1]
    t2 = d[2]
    if not (t1[1].isalpha() and t2[1].isalpha()): # Delete the illegal word
        return False
    if d[0] == 'ADVMOD' and (t1[2] in VERB_TYPES + ADJ_TYPES + ADV_TYPES and t2[2] in ADV_TYPES): #'mod'
        return True
    if d[0] == 'AMOD' and (t1[2] in NOUN_TYPES and t2[2] in ADJ_TYPES): #'mod'
        return True
    if d[0] == 'COMPOUND' and (t1[2] in NOUN_TYPES and t2[2] in NOUN_TYPES): #'mod'
        return True
    if d[0] == 'NSUBJ' and (t1[2] in VERB_TYPES and t1[1] != 'be' and t2[2] in NOUN_TYPES): #'sv'
        return True
    if (d[0] == 'DOBJ' or d[0] == 'IOBJ' or d[0] == 'NSUBJPASS') and (t1[2] in VERB_TYPES and t2[2] in NOUN_TYPES): #'vo'
        return True
    if d[0] == 'COMPOUND:PRT' and (t2[2] in ADV_TYPES + PREP_TYPES and t1[2] in VERB_TYPES): # prep
        return True
    if d[0] == 'CASE' and (t2[2] in ADV_TYPES + PREP_TYPES and t1[2] in NOUN_TYPES): # prep
        return True
    if d[0] == 'MWE' and (t2[2] in ADV_TYPES + PREP_TYPES and  t1[2] in ADV_TYPES + PREP_TYPES): # prep
        return True
    return False

def _convert_dep(d):
    t1 = d[3]
    t2 = d[4]
    if d[0] == 'NSUBJ':
        return (1, d[2], d[1])  #'sv'
    if d[0] == 'DOBJ' or d[0] == 'IOBJ' or d[0] == 'NSUBJPASS':
        return (2, d[1], d[2])  #'vo'
    if d[0] == 'AMOD' or d[0] == 'ADVMOD' or d[0] == 'COMPOUND': 
        return (3, d[2], d[1])  #'mod'
    if d[0] == 'COMPOUND:PRT' or d[0] == 'MWE':
        return (4, d[1], d[2])  #'prep'
    if d[0] == 'CASE':
        return (4, d[2], d[1])  #'prep'
    return None

def process_conll_file(text):
    # conll file format:
    # 1  Assimilation  assimilation  NN  _  3  nsubj
    # 1  3  nsubj  =  nsubj(noun-3, verb-1)
    poss, dep = ['NONE'] * len(text), '0'
    tokens = [process_conll_line(l) for l in text]
    for i, t in enumerate(tokens):
        assert t['i'] == i, 't[i] = %d, i = %d' % (t['_id'], i)
        td = tokens[t['di']]
        if is_esl_dep(t['dt'], td, t):
            dep = convert_dep(t['dt'], td, t)['dt']
        del t['dt'], t['di']
    poss = [t['pt'] if t['pt'] else 'NONE' for t in tokens]
    dep = dep if len(text) < 3 else '0'
    return poss, dep

def process_conll_line(tt):
    assert len(tt) == 7, 'len(%s) = %d != 7' % (repr(tt), len(tt))
    tt[2] = tt[2].lower()   # lemmas are in lower case
    pt = tt[3].upper()
    dt = tt[6].upper()

    return {'i': int(tt[0])-1, 't': tt[1], 'l': tt[2], 'pt': pt, 'di': int(tt[5])-1, 'dt': dt}

@timeit
def lemmatize(s, timeout=10):  # TODO: rename to nlp_parse
    '''
    s: a English string
    return: a list of lower-cased lemmas
    '''

    try:
        conll = requests.post(LEMMATIZER_URL, s.encode('utf-8'), timeout=timeout).text  # may end with \r\n
        lines = [line.strip() for line in conll.split('\n')]
        tokens = [line.split('\t') for line in lines if line]
        poss, dep = process_conll_file(tokens)
        logger.info('conll: "%s" -> %s', s, tokens)
        ll = [t[2].lower() for t in tokens]
        ref = [t[1] for t in tokens]
    except Exception as e:
        logger.exception('Failed to lemmatize "%s"', s)
        ll = ref = s.split()
        ll = [l.lower() for l in ll]
        poss, dep = ['NONE'] * len(ll), '0'
    return ll, ref, poss, dep

lemmatize('checking')

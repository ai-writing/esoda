from common.mongodb import MONGODB
POS2POS = {'verb': [u'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'], 'preposition': ['IN', 'TO'], 'adverb': ['RB', 'RBR', 'RBS', 'RP'],
    'adjective': ['JJ', 'JJR', 'JJS'], 'noun': ['NN', 'NNP', 'NNPS', 'NNS']}

def entry(word):
    return MONGODB.common.thesaurus_mix_asin.find_one({'_id': word})

def meanings(word):
    entry = MONGODB.common.thesaurus_mix_asin.find_one({'_id': word})
    if entry:
        l = [(meaning['pos'], meaning['exp']) for meaning in entry['meaning']]
        return l
    else:
        return []

def synonyms(word, score = 0, pos = None, exp = None, max_count = None):
    entry = MONGODB.common.thesaurus_mix_asin.find_one({'_id': word})
    if entry:
        l = []
        meanings = entry['meaning_former'] if entry.get('meaning_former') else entry['meaning']
        for m in meanings:
            temp = []
            if (m['pos'] in POS2POS and pos in POS2POS[m['pos']]) or pos == 'NONE':
                temp = [(syn['w'], syn['s']) for syn in m['syn'] if len(syn['w'].split()) < 2] # syn must be a word not a phrase for now
                temp.sort(cmp = lambda (w1, s1), (w2, s2): cmp(s1, s2), reverse = True)
                max_score_list_length = [t[1] for t in temp].count(max(t[1] for t in temp))
                l += temp[:15] if max_score_list_length < 15 else temp[:max_score_list_length]
        # l = sorted(dict(l).iteritems(), key= lambda x: x[1], reverse=True)
        l = list(set([w for (w,s) in l if w != word]))
        if max_count== None or max_count <= 0:
            return l
        else:
            return l[:max_count+1]
    else:
        return []

def antonyms(word, score = 0, pos = None, exp = None, max_count = None):
    entry = MONGODB.common.thesaurus_mix_asin.find_one({'_id': word})
    if entry:
        l = []
        for m in entry['meaning']:
            if (pos == None or m['pos'] == pos.lower()) and (exp == None or exp.lower() in m['exp']):
                l.extend([(ant['w'], ant['s']) for ant in m['ant'] if ant['s'] >= score])
        l.sort(cmp = lambda (w1, s1), (w2, s2): cmp(s1, s2), reverse = True)
        l = [w for (w, s) in l]
        if max_count== None or max_count <= 0:
            return l
        else:
            return l[:max_count]
    else:
        return []

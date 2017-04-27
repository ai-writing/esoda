from django.conf import settings

mongo = settings.MONGODB

def entry(word):
    return mongo.common.thesaurus.find_one({'_id': word})

def meanings(word):
    entry = mongo.common.thesaurus.find_one({'_id': word})
    if entry:
        l = [(meaning['pos'], meaning['exp']) for meaning in entry['meaning']]
        return l
    else:
        return []

def synonyms(word, score = 0, pos = None, exp = None, max_count = None):
    entry = mongo.common.thesaurus.find_one({'_id': word})
    if entry:
        l = []
        for m in entry['meaning']:
            if (pos == None or m['pos'] == pos.lower()) and (exp == None or exp.lower() in m['exp']):
                l.extend([(syn['w'], syn['s']) for syn in m['syn'] if syn['s'] >= score])
        l.sort(cmp = lambda (w1, s1), (w2, s2): cmp(s1, s2), reverse = False)
        l = sorted(dict(l).iteritems(), key= lambda x: x[1], reverse=True)
        l = [w for (w, s) in l]
        if word in l:
            l.remove(word)
        l.insert(0, word)
        if max_count== None or max_count <= 0:
            return l
        else:
            return l[:max_count+1]
    else:
        return []

def antonyms(word, score = 0, pos = None, exp = None, max_count = None):
    entry = mongo.common.thesaurus.find_one({'_id': word})
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

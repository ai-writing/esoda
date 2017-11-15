# -*- coding: utf-8 -*-
import os
from pymongo import InsertOne,ReplaceOne,MongoClient
import json
ESL_DEP_TYPES = ['NSUBJ', 'DOBJ', 'IOBJ', 'NSUBJPASS', 'AMOD', 'NN', 'ADVMOD', 'PARTMOD', 'PREP', 'POBJ', 'PRT'
,'COMPOUND','COMPOUND:PRT','CASE']  #'NMOD'TODO……

VERB_TYPES = ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']
PREP_TYPES = ['IN', 'TO']
ADV_TYPES = ['RB', 'RBR', 'RBS', 'RP']
ADJ_TYPES = ['JJ', 'JJR', 'JJS']
NOUN_TYPES = ['NN', 'NNP', 'NNPS', 'NNS']
# COLLOCATIONS = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']

dbc= MongoClient('166.111.139.42')
db = dbc.admin
db.authenticate('root', 'root')
poss = list(dbc.common.poss.find())
pt2i = dict([(p['pt'], p['_id']) for p in poss])
info=json.load(open('info.json'))


def is_esl_dep(dt, t, td):
	#print t
	return _is_esl_dep((dt, None, None, (None, t['l'], t['pt']), (None, td['l'], td['pt'])))

def convert_dep(dt, t, td):
    dt, t1, t2 = _convert_dep((dt, t, td, (None, t['l'], t['pt']), (None, td['l'], td['pt'])))
    return {'dt': str(dt), 'l1': t1['l'], 'i1': str(t1['i']), 'l2': t2['l'], 'i2': str(t2['i'])}

def save_info():
	info={}
	res=dbc.crawl.try2.find()
	for r in res:
		info[r['_id']]=r['vName']
	f=open('info.json','w')
	json.dump(info, f)
	f.close()

# format of d:
# (type, None, None, token1, token2)
# format of token:
# (~word, lemma, pos)
def _is_esl_dep(d):
    if d[0] not in ESL_DEP_TYPES:
        return False
    t1 = d[3]   #TODO: filter out numbers
    t2 = d[4]   #TODO: filter out numbers
    if (t1[2] in VERB_TYPES and t1[1] == 'be') or (t2[2] in VERB_TYPES and t2[1] == 'be'):
        return False
    if d[0] == 'NSUBJ' and not (t1[2] in VERB_TYPES + ADJ_TYPES and t2[2] in NOUN_TYPES):
        return False
    if (d[0] == 'DOBJ' or d[0] == 'IOBJ' or d[0] == 'NSUBJPASS') and not (t1[2] in VERB_TYPES and t2[2] in NOUN_TYPES):
        return False
    if d[0] == 'ADVMOD' and not (t1[2] in VERB_TYPES + ADJ_TYPES + ADV_TYPES and t2[2] in ADV_TYPES):
        return False
    if d[0] == 'PARTMOD' and not (t1[2] in NOUN_TYPES and t2[2] in VERB_TYPES):
        return False
    if d[0] == 'PREP' and not (t2[2] in PREP_TYPES):
        return False
    if d[0] == 'POBJ' and not (t1[2] in PREP_TYPES):
        return False
    if d[0] == 'PRT' and not (t1[2] in VERB_TYPES and t2[2] in PREP_TYPES + ADV_TYPES):
        return False
    if d[0] == 'COMPOUND' and not (t1[2] in NOUN_TYPES and t2[2] in NOUN_TYPES):
        return False
    if d[0] == 'COMPOUND:PRT' and not (t2[2] in ADV_TYPES + PREP_TYPES and t1[2] in VERB_TYPES):
        return False
    if d[0] == 'CASE' and not (t2[2] in PREP_TYPES and t1[2] in NOUN_TYPES):
        return False
    return True

def _convert_dep(d):
    t1 = d[3]
    t2 = d[4]
    if d[0] == 'NSUBJ' and t1[2] in VERB_TYPES:
        return (1, d[2], d[1])  #'sv'
    if d[0] == 'DOBJ' or d[0] == 'IOBJ' or d[0] == 'NSUBJPASS':
        return (2, d[1], d[2])  #'vo'
    if d[0] == 'AMOD' or d[0] == 'NN' or d[0] == 'ADVMOD':
        return (3, d[2], d[1])  #'mod'
    if d[0] == 'PARTMOD' or d[0] == 'NSUBJ':
        return (3, d[1], d[2])  #'mod'
    if d[0] == 'PREP' or d[0] == 'PRT'or d[0] == 'COMPOUND:PRT':
        return (4, d[1], d[2])  #'prep'
    if d[0] == 'POBJ':
        return (4, d[1], d[2])  #'prep'
    if d[0] == 'COMPOUND':
        return (3, d[2], d[1])  #'mod'
    if d[0] == 'CASE':
        return (4, d[2], d[1])  #'prep'
    #return None


def main_procedure():
	root='./parsed/'
	for name in os.listdir(root):
		pid=name[:-6]
		path = root+name
		with open(path, 'r') as fin:
			text = fin.read()
		#print text
		_sentences = process_conll_file(pid, text)
		if not os.path.exists('./'+info[pid]):
    		os.mkdir('./'+info[pid])
		
		f=open('./'+info[pid]+'/'+pid+'.json','w')
		for s in _sentences:
			s['c']=info[pid]
			#print s
			json.dump({"index":{"_index":"sentences", '_type':info[pid]}}, f)
			f.write('\n')
			json.dump(s, f)
			f.write('\n')
				
		f.close()

		try:
			with open(path, 'r') as fin:
				text = fin.read()
			#print text
			_sentences = process_conll_file(pid, text)
			for s in _sentences:
				s['c']=venue
				#print s
				sentences.append({'_index': 'test', '_type': 'sentences', '_source': s})
			f=open('./json/'+pid+'.json','w')
			f.write(sentences)
			f.close()
		except Exception as e:
			print 'Exception when counting:', repr(e)

def process_conll_file(uid, text, token_dict=None, pos_dict=None, dep_dict=None):
	# conll file format:
	# 1  Assimilation  assimilation  NN  _  3  nsubj
	# 1  3  nsubj  =  nsubj(noun-3, verb-1)
	sentences = []
	
	for s in text.split('\n\n'):
		if not (s and s.strip()):
			continue
		tokens = [process_conll_line(l, token_dict, pos_dict, dep_dict) for l in s.split('\n') if l !='\n']
		#print tokens
		deps = []
		token=[]
		for i, t in enumerate(tokens):
			assert t['i'] == i, 't[i] = %d, i = %d' % (t['_id'], i)
			td = tokens[t['di']]
			if is_esl_dep(t['dt'], td, t):
				deps.append(convert_dep(t['dt'], td, t))
			del t['dt'], t['di']#,t['i'],t['pt']
			token.append({'t':t['t'],'l':t['l']})
		sentences.append({'p': uid,'t': token, 'd': deps})
	return sentences

def process_conll_line(l, token_dict, pos_dict, dep_dict):
	#print 'nihao '+l
	tt = l.split('\t')
	assert len(tt) == 7, 'len(%s) = %d != 7' % (repr(tt), len(tt))
	tt[2] = tt[2].lower()	# lemmas are in lower case!
	if token_dict is not None:
		token_dict[tt[1]] = token_dict.get(tt[1], 0)	# count word
		token_dict[tt[2]] = token_dict.get(tt[2], 0) + 1	# count lemma
	pt = tt[3].upper()
	dt = tt[6].upper()
	if pos_dict is not None:
		pos_dict[pt] = pos_dict.get(pt, 0) + 1	# count pos type
	if dep_dict is not None:
		dep_dict[dt] = dep_dict.get(dt, 0) + 1	# count dep type
	return {'i': int(tt[0])-1, 't': tt[1], 'l': tt[2], 'pt': pt, 'di': int(tt[5])-1, 'dt': dt}


if __name__ == "__main__":
	main_procedure()

# -*- coding: utf-8 -*-
import os,sys
from pymongo import UpdateOne,MongoClient

dbc= MongoClient('166.111.139.42')
db=dbc.admin
db.authenticate('root', 'root')
db = dbc.common

res=set([s['t'] for s in db.tokens.find()])
argin=[]
argadd=[]
num=0
zidian={}
if __name__ == "__main__":
	root='./parsed/'
	print 'Start'
	for name in os.listdir(root):		
		for line in open(os.path.join(root, name)):  
			if line !='\n':				
				sen=line.split('\t')
				if len(sen)>3:	
					if zidian.get(sen[2].lower())==None:
						zidian[sen[2].lower()]=1
					else:
						zidian[sen[2].lower()]=zidian.get(sen[2].lower())+1
					
					if sen[1]!=sen[2].lower():
						zidian[sen[1]]=0
	print 'Sorting'

	count=db.tokens.count()

	#tmp=sorted(Counter(lemma).items(), key=lambda x:x[1],reverse=True)	
	tmp=sorted(zidian.iteritems(), key=lambda d:d[1], reverse = True )
	# tmp = sorted(zidian.items(), key=operator.itemgetter(1),reverse=True)
	for c in tmp:
		if c[0] in res and c[1]!=0:
			argadd.append(UpdateOne({'t':c[0]}, {'$inc': {'tf': c[1]}}))
		elif c[0] not in res and c[1] == 0:
			count+=1
			argin.append({'_id':count,'tf': 0,'t':c[0]})

	print 'Operate db'
	if argadd:
		db.tokens.bulk_write(argadd)
		print 'increase over',len(argadd)
	if argin:
		db.tokens.insert(argin)
		print 'insert over',len(argin)
	
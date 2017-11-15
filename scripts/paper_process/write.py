# -*- coding: utf-8 -*-
import time
import os

from pymongo import UpdateOne,MongoClient

dbc= MongoClient('166.111.139.42')
db=dbc.admin
db.authenticate('root', 'root')
db = dbc.dblp

def p2t_write(pdf_dir):
	f=open('p2t.bat','w')
	list_file=os.listdir(pdf_dir)
	for name in list_file:
		f.write('pdftotext.exe -enc ASCII7 -eol unix -nopgbrk '+os.path.join(pdf_dir,name)
			+' extracted/'+name[:-4]+'.txt\n')
	f.close()

def parse_write(pdf_dir):
	f=open('parse.bat','w')
	list_file=os.listdir(pdf_dir)
	for name in list_file:
		f.write(java -cp "stanford-corenlp-full-2016-10-31/*" -Xmx12g edu.stanford.nlp.pipeline.StanfordCoreNLP 
			-props "esl_paper.properties" -filelist tolist.txt -outputDirectory parsed 2> result.txt)
	f.close()

def list_write(pdf_dir):
	f=open('tolist.txt','w')
	list_file=os.listdir(pdf_dir)
	for name in list_file:
		f.write(os.path.join(pdf_dir,name)+'\n')
	f.close()

if __name__ == "__main__":
	p2t_write('paper/')
	list_write('refined/')
	#parse_write()
	
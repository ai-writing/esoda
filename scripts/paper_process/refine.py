# -*- coding: utf-8 -*-
import os, re
from nltk.tokenize.stanford import StanfordTokenizer
from nltk.tokenize import sent_tokenize, word_tokenize
import sys
reload(sys)
sys.setdefaultencoding('utf8')
def absref( lines ):	#txt中是否有referenc 或者 bibliography（参考文献）
	cnt = 0
	for line in lines:
		if not line: continue
		line = line.lower()
		if line.find('reference') != -1 or line.find('bibliography') != -1: cnt += 1

	if cnt == 0:
		( filepath, filename ) = os.path.split(dest_file)
		print "No references: " + filename
		return False
	return True


def paralength( lines ):	#txt段落长度是否足够（需平均大于60且300字符以上超过10段）
	total = 0
	lcnt = 0
	para = 0
	
	for line in lines:
		if not line: continue
		lcnt += 1
		length = len(line)
		total += length
		if length > 300:
			para += 1

	if lcnt == 0:
		( filepath, filename ) = os.path.split(dest_file)
		print 'Empty txt: ' + filename
		return False
	else:
		average = float(total)/float(lcnt)
		if average < 60:
			if para <= 10:
				( filepath, filename ) = os.path.split(dest_file)
				print "Low paralength: " + filename
				return False
	return True


import string
def check_text_format(text):	# 判断是否包含过多非法字符
	if not text:
		return False
	valid_chars = 0
	for i in text:
		if i in string.printable:
			valid_chars += 1
	# TODO: log valid_chars and len(text)
	return float(valid_chars)/len(text) > 0.6


def checkpdfbytxt( lines ):	#通过txt大致判断是否是合格论文
	if not check_text_format( lines ): return False
	if not paralength( lines ): return False
	if not absref( lines ): return False
	return True


def wordnum( line, minn ):	#该句line中词数需大于minn
	words = line.split(' ')
	cnt = 0
	for word in words:
		if word != '':
			cnt += 1

	if cnt <= minn:
		# print line
		return False
	return True 

def notended( line ):	#判断该句是否结束
	length = len(line)
	if line[length-1].isalpha() or line[length-1].isdigit(): #以数字或字母结尾
		# print line
		return False

	if line[length-2] == ' ': #倒数第二个字符是空格（正常.？！会紧跟单词）
		# print line
		return False
		
	cnt1 = 0
	for i in range(length):	#匹配左右括号
		if line[i] == '(' or line[i] == '[' or line[i] == '{': cnt1 += 1
		elif line[i] == ')' or line[i] == ']' or line[i] == '}': cnt1 -= 1
		if cnt1 < 0: return False

	if cnt1 != 0:
		# print line
		return False
	return True

def averageword( line , minl, maxl ):	#平均单词长度需要大于minl小于maxl
	words = line.split(' ')
	total = 0
	cntwd = 0
	for word in words:
		if word == '': continue
		total += len(word)
		cntwd += 1

	average = float(total) / float(cntwd) if cntwd else 0
	if average < minl:
		# print average
		# print line
		return False
	if average > maxl:
		# print average
		# print line
		return False
	return True

def formulas( line, ratio ):	#非字母比例不得超过ratio
	total = 0
	cnt = 0
	length = len(line)
	for i in range(length):
		if line[i] == ' ': continue
		total += 1
		if line[i].isalpha() != True: cnt += 1

	average = float(cnt) / float(total)
	if average > ratio:
		# print average
		# print line
		return False
	return True


def bigCharas( line, ratio ):	#大写字母比例不得超过ratio
	total = 0
	cnt = 0
	length = len(line)
	for i in range(length):
		if line[i] == ' ': continue
		if line[i].isalpha() != True: continue
		total += 1
		if line[i].isupper(): cnt += 1

	average = float(cnt) / float(total)
	if average > ratio:
		# print average
		# print line
		return False
	return True


def startwithlower(line):	#句子不得以小写字母或符号开头
	if line[0].islower():
		# print line
		return False
	# if line[0].isalpha() == False and line[0].isdigit() == False:
	# 	print line
	# 	return False
	return True

def refine_para(line):	#判断段落是否合格
	if averageword( line, 3, 10 ) == False: return False
	if formulas( line, 0.2 ) == False: return False
	if bigCharas( line, 0.2 ) == False: return False
	return True

def refine_sent(line):	#判断句子是否合格
	if averageword( line, 2, 10 ) == False: return False
	if wordnum( line, 3 ) == False: return False
	if formulas( line, 0.2 ) == False: return False
	if bigCharas( line, 0.4 ) == False: return False
	if notended( line ) == False: return False
	if startwithlower(line) == False: return False
	return True


def sentsfromparas( paras ):	#从很多段落中提取句子
	sents = []
	for line in paras:
		if not line: continue
		line = line.strip('\n')
		line = line.strip('\r')

		sentences = sent_tokenize(line)
		
		for sentence in sentences:
			if refine_sent(sentence) == False: continue
			sents.append(sentence)
	return sents


def getbigparas( lines ):	#从txt中提取段落
	paras = []
	for line in lines:
		if len(line) > 300:
			if refine_para(line) == False: continue
			paras.append(line)
	return paras

def writeto( sents, paperid, to_folder ):	#把获得的句子按格式写入to_folder文件夹中
	name = str(paperid) + '.txt'
	dest_file = os.path.join( to_folder, name )
	with open( dest_file, 'w' ) as f:
		for sent in sents:
			# tokens = StanfordTokenizer().tokenize(sent)	#效率过低
			tokens = word_tokenize(sent)

			for token in tokens:
				f.write( token + ' ' )
			f.write('\n')


def _toRemove(line):
	if line == '': return True
	if not (line[0].isupper() or line[0].isdigit()) or \
		line.startswith('ACM Classification :') or \
		line.startswith('Keywords :') or \
		line.startswith('To copy otherwise ,') or \
		line.startswith('Permission to make digital or hard copies') or \
		('<' in line and '>' in line):	# HTML tags
		return True
	m = re.match(r'Copyright \d{4} ACM', line)
	if m:
		return True
	m = re.search(r'http:\\/\\/', line)
	if m:
		return True
	m = re.search(r'(Figure|Fig|Table|Tab) \d+ :', line)
	if m:
		return True
	m = re.search(r'[^\.\?!\'"].Permission', line)
	if m:
		return True
	if len(line.split()) <= 4:
		return True
	return False


def refine_lines(sentences):
	lineList=[filter(lambda c: ord(c) < 128, s.replace(u'\xa0', u' ')) for s in sentences]
	resultLineList=[]
	for line in lineList:
		if len(line) > 0:
			line = re.sub(r'-LRB-.*?-RRB-', '', line)
			line = re.sub(r'-LRB-', '', line)
			line = re.sub(r'-RRB-', '', line)
			line = re.sub(r'-LSB-.*?-RSB-', '', line)
			line = re.sub(r'-LSB-', '', line)
			line = re.sub(r'-RSB-', '', line)
			line = re.sub(r'\(.*?\)', '', line)
			line = re.sub(r'\(', '', line)
			line = re.sub(r'\)', '', line)
			line = re.sub(r'\[.*?\]', '', line)
			line = re.sub(r'\[', '', line)
			line = re.sub(r'\]', '', line)
			if _toRemove(line):
				if line != '\n':
					# print line[0:-1]
					pass
			else:
				resultLineList.append(line)
	return resultLineList


def changestatus( paperid, status ):	#更改服务器中paper状态为status #待填补
	return


def refine(text):
	lines = [l for l in text.split('\n') if l]
	paras = getbigparas(lines)
	sents = sentsfromparas(paras)
	sents = refine_lines(sents)
	# writeto( sents, paperid, to_folder )
	return ''.join([l + '\n' for l in sents if l])


def start(root,out):
	import sys
	for name in os.listdir(root):
		with open(os.path.join(root, name)) as fin:
			#print fin
			text = fin.read()
		refined = refine(text)
		print name, len(refined.split())
		if not refined:
			continue
		with open(os.path.join(out, name), 'w') as fout:
			fout.write(refined)

start('extracted','refined')

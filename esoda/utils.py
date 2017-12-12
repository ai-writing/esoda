# -*- coding: utf-8 -*-
from .paper import mongo_get_objects, DblpPaper
import re
import string
import logging

logger = logging.getLogger(__name__)

DEPS_VIEW = {u'(主谓) *': u' + 动词', u'* (主谓)': u'主语 + ', u'(动宾) *': u' + 宾语', u'* (动宾)': u'动词 + ',
    u'(修饰) *': u' + 被修饰词', u'* (修饰)': u'修饰 + ', u'(介词) *': u' + 介词', u'* (介词)': u'介词 + '}
EN_PUNC = string.punctuation
CH_PUNC = u'《》（）&%￥#@！{}【】'
PUNC = EN_PUNC + CH_PUNC
TRANS_TABLE = dict((ord(c), u' ') for c in PUNC)


CORPUS = {"0": [{"i": "bnc", "d": "bnc",'n':"BNC"}], "1": [{'i': 'conf/sc', 'score': 159, 'd': 'dblp', 'n': 'SC'}, {'i': 'conf/asplos', 'score': 158, 'd': 'dblp', 'n': 'ASPLOS'}, {'i': 'conf/isca', 'score': 156, 'd': 'dblp', 'n': 'ISCA'}, {'i': 'conf/cnhpca', 'score': 154, 'd': 'dblp', 'n': 'HPCA'}, {'i': 'conf/fast', 'score': 148, 'd': 'dblp', 'n': 'FAST'}, {'i': 'conf/ppopp', 'score': 143, 'd': 'dblp', 'n': 'PPOPP'}, {'i': 'conf/usenix', 'score': 127, 'd': 'dblp', 'n': 'USENIX'}, {'i': 'conf/cloud', 'score': 38, 'd': 'dblp', 'n': 'SOCC'}, {'i': 'conf/eurosys', 'score': 37, 'd': 'dblp', 'n': 'EUROSYS'}, {'i': 'conf/icdcs', 'score': 36, 'd': 'dblp', 'n': 'ICDCS'}, {'i': 'conf/date', 'score': 35, 'd': 'dblp', 'n': 'DATE'}, {'i': 'conf/ipps', 'score': 34, 'd': 'dblp', 'n': 'IPDPS'}, {'i': 'conf/eurodac', 'score': 33, 'd': 'dblp', 'n': 'DAC'}, {'i': 'conf/hpdc', 'score': 30, 'd': 'dblp', 'n': 'HPDC'}, {'i': 'conf/IEEEpact', 'score': 28, 'd': 'dblp', 'n': 'PACT'}, {'i': 'conf/sigmetrics', 'score': 26, 'd': 'dblp', 'n': 'SIGMETRICS'}, {'i': 'conf/cgo', 'score': 23, 'd': 'dblp', 'n': 'CGO'}, {'i': 'conf/ics', 'score': 23, 'd': 'dblp', 'n': 'ICS'}, {'i': 'conf/iccad', 'score': 21, 'd': 'dblp', 'n': 'ICCAD'}, {'i': 'conf/podc', 'score': 20, 'd': 'dblp', 'n': 'PODC'}, {'i': 'conf/spaa', 'score': 20, 'd': 'dblp', 'n': 'SPAA'}, {'i': 'conf/codes', 'score': 19, 'd': 'dblp', 'n': 'CODES'}, {'i': 'conf/fpga', 'score': 19, 'd': 'dblp', 'n': 'FPGA'}, {'i': 'conf/icpp', 'score': 19, 'd': 'dblp', 'n': 'ICPP'}, {'i': 'conf/vee', 'score': 19, 'd': 'dblp', 'n': 'VEE'}, {'i': 'conf/mss', 'score': 16, 'd': 'dblp', 'n': 'MSST'}, {'i': 'conf/itc', 'score': 15, 'd': 'dblp', 'n': 'ITC'}, {'i': 'conf/hipeac', 'score': 14, 'd': 'dblp', 'n': 'HIPC'}, {'i': 'conf/iccd', 'score': 12, 'd': 'dblp', 'n': 'ICCD'}, {'i': 'conf/lisa', 'score': 10, 'd': 'dblp', 'n': 'LISA'}, {'i': 'conf/parco', 'score': 7, 'd': 'dblp', 'n': 'PARCO'}, {'i': 'conf/rtas', 'score': 3, 'd': 'dblp', 'n': 'RTAS'}, {'i': 'conf/performance', 'score': 0, 'd': 'dblp', 'n': 'PERFORMANCE'}, {'i': 'journals/tpds', 'score': 175, 'd': 'dblp', 'n': 'TPDS'}, {'i': 'journals/tc', 'score': 156, 'd': 'dblp', 'n': 'TOC'}, {'i': 'journals/micro', 'score': 152, 'd': 'dblp', 'n': 'MICRO'}, {'i': 'journals/tcad', 'score': 150, 'd': 'dblp', 'n': 'TCAD'}, {'i': 'journals/tos', 'score': 139, 'd': 'dblp', 'n': 'TOS'}, {'i': 'journals/tocs', 'score': 138, 'd': 'dblp', 'n': 'TOCS'}, {'i': 'journals/tvlsi', 'score': 35, 'd': 'dblp', 'n': 'TVLSI'}, {'i': 'journals/jpdc', 'score': 30, 'd': 'dblp', 'n': 'JPDC'}, {'i': 'journals/jsa', 'score': 21, 'd': 'dblp', 'n': 'JSA'}, {'i': 'journals/pe', 'score': 21, 'd': 'dblp', 'n': 'PE'}, {'i': 'journals/tecs', 'score': 20, 'd': 'dblp', 'n': 'TECS'}, {'i': 'journals/taco', 'score': 18, 'd': 'dblp', 'n': 'TACO'}, {'i': 'journals/taas', 'score': 14, 'd': 'dblp', 'n': 'TAAS'}, {'i': 'journals/todaes', 'score': 14, 'd': 'dblp', 'n': 'TODAES'}, {'i': 'journals/trets', 'score': 13, 'd': 'dblp', 'n': 'TRETS'}] ,"2": [{'i': 'conf/infocom', 'score': 189, 'd': 'dblp', 'n': 'INFOCOM'}, {'i': 'conf/sigcomm', 'score': 169, 'd': 'dblp', 'n': 'SIGCOMM'}, {'i': 'conf/mobicom', 'score': 157, 'd': 'dblp', 'n': 'MOBICOM'}, {'i': 'conf/nsdi', 'score': 52, 'd': 'dblp', 'n': 'NSDI'}, {'i': 'conf/imc', 'score': 41, 'd': 'dblp', 'n': 'IMC'}, {'i': 'conf/mobisys', 'score': 40, 'd': 'dblp', 'n': 'MOBISYS'}, {'i': 'conf/sensys', 'score': 33, 'd': 'dblp', 'n': 'SENSYS'}, {'i': 'conf/ipsn', 'score': 30, 'd': 'dblp', 'n': 'IPSN'}, {'i': 'conf/conext', 'score': 28, 'd': 'dblp', 'n': 'CONEXT'}, {'i': 'conf/mobihoc', 'score': 23, 'd': 'dblp', 'n': 'MOBIHOC'}, {'i': 'conf/icnp', 'score': 21, 'd': 'dblp', 'n': 'ICNP'}, {'i': 'conf/iwqos', 'score': 16, 'd': 'dblp', 'n': 'IWQOS'}, {'i': 'conf/secon', 'score': 15, 'd': 'dblp', 'n': 'SECON'}, {'i': 'conf/nossdav', 'score': 14, 'd': 'dblp', 'n': 'NOSSDAV'}, {'i': 'journals/ton', 'score': 175, 'd': 'dblp', 'n': 'TON'}, {'i': 'journals/tmc', 'score': 173, 'd': 'dblp', 'n': 'TMC'}, {'i': 'journals/jsac', 'score': 171, 'd': 'dblp', 'n': 'JSAC'}, {'i': 'journals/twc', 'score': 61, 'd': 'dblp', 'n': 'TWC'}, {'i': 'journals/tcom', 'score': 46, 'd': 'dblp', 'n': 'TOC'}, {'i': 'journals/cn', 'score': 39, 'd': 'dblp', 'n': 'CN'}, {'i': 'journals/tosn', 'score': 28, 'd': 'dblp', 'n': 'TOSN'}, {'i': 'journals/toit', 'score': 12, 'd': 'dblp', 'n': 'TOIT'}] ,"3": [{'i': 'conf/sp', 'score': 169, 'd': 'dblp', 'n': 'SP'}, {'i': 'conf/ccs', 'score': 164, 'd': 'dblp', 'n': 'CCS'}, {'i': 'conf/uss', 'score': 161, 'd': 'dblp', 'n': 'USS'}, {'i': 'conf/eurocrypt', 'score': 150, 'd': 'dblp', 'n': 'EUROCRYPT'}, {'i': 'conf/crypto', 'score': 144, 'd': 'dblp', 'n': 'CRYPTO'}, {'i': 'conf/ndss', 'score': 36, 'd': 'dblp', 'n': 'NDSS'}, {'i': 'conf/acsac', 'score': 29, 'd': 'dblp', 'n': 'ACSAC'}, {'i': 'conf/ches', 'score': 26, 'd': 'dblp', 'n': 'CHES'}, {'i': 'conf/asiacrypt', 'score': 22, 'd': 'dblp', 'n': 'ASIACRYPT'}, {'i': 'conf/csfw', 'score': 22, 'd': 'dblp', 'n': 'CSFW'}, {'i': 'conf/dsn', 'score': 21, 'd': 'dblp', 'n': 'DSN'}, {'i': 'conf/pkc', 'score': 21, 'd': 'dblp', 'n': 'PKC'}, {'i': 'conf/esorics', 'score': 20, 'd': 'dblp', 'n': 'ESORICS'}, {'i': 'conf/raid', 'score': 20, 'd': 'dblp', 'n': 'RAID'}, {'i': 'conf/tcc', 'score': 19, 'd': 'dblp', 'n': 'TCC'}, {'i': 'conf/fse', 'score': 18, 'd': 'dblp', 'n': 'FSE'}, {'i': 'conf/srds', 'score': 16, 'd': 'dblp', 'n': 'SRDS'}, {'i': 'journals/tifs', 'score': 163, 'd': 'dblp', 'n': 'TIFS'}, {'i': 'journals/tdsc', 'score': 151, 'd': 'dblp', 'n': 'TDSC'}, {'i': 'journals/joc', 'score': 143, 'd': 'dblp', 'n': 'JOC'}, {'i': 'journals/compsec', 'score': 27, 'd': 'dblp', 'n': 'COMPSEC'}, {'i': 'journals/tissec', 'score': 23, 'd': 'dblp', 'n': 'TISS'}, {'i': 'journals/jcs', 'score': 21, 'd': 'dblp', 'n': 'JCS'}, {'i': 'journals/dcc', 'score': 14, 'd': 'dblp', 'n': 'DCC'}] ,"4": [{'i': 'conf/icse', 'score': 163, 'd': 'dblp', 'n': 'ICSE'}, {'i': 'conf/pldi', 'score': 156, 'd': 'dblp', 'n': 'PLDI'}, {'i': 'conf/popl', 'score': 156, 'd': 'dblp', 'n': 'POPL'}, {'i': 'conf/osdi', 'score': 153, 'd': 'dblp', 'n': 'OSDI'}, {'i': 'conf/kbse', 'score': 150, 'd': 'dblp', 'n': 'ASE'}, {'i': 'conf/oopsla', 'score': 148, 'd': 'dblp', 'n': 'OOPSLA'}, {'i': 'conf/sosp', 'score': 145, 'd': 'dblp', 'n': 'SOSP'}, {'i': 'conf/sigsoft', 'score': 120, 'd': 'dblp', 'n': 'ESEC'}, {'i': 'conf/icws', 'score': 26, 'd': 'dblp', 'n': 'ICWS'}, {'i': 'conf/issta', 'score': 25, 'd': 'dblp', 'n': 'ISSTA'}, {'i': 'conf/ecoop', 'score': 24, 'd': 'dblp', 'n': 'ECOOP'}, {'i': 'conf/icsm', 'score': 24, 'd': 'dblp', 'n': 'ICSM'}, {'i': 'conf/icfp', 'score': 21, 'd': 'dblp', 'n': 'ICFP'}, {'i': 'conf/icsoc', 'score': 21, 'd': 'dblp', 'n': 'ICSOC'}, {'i': 'conf/re', 'score': 21, 'd': 'dblp', 'n': 'RE'}, {'i': 'conf/iwpc', 'score': 20, 'd': 'dblp', 'n': 'ICPC'}, {'i': 'conf/middleware', 'score': 19, 'd': 'dblp', 'n': 'MIDDLEWARE'}, {'i': 'conf/caise', 'score': 18, 'd': 'dblp', 'n': 'CAISE'}, {'i': 'conf/esem', 'score': 18, 'd': 'dblp', 'n': 'ESEM'}, {'i': 'conf/issre', 'score': 18, 'd': 'dblp', 'n': 'ISSRE'}, {'i': 'conf/sas', 'score': 18, 'd': 'dblp', 'n': 'SAS'}, {'i': 'conf/vmcai', 'score': 18, 'd': 'dblp', 'n': 'VMCAI'}, {'i': 'conf/wcre', 'score': 18, 'd': 'dblp', 'n': 'WCRE'}, {'i': 'conf/models', 'score': 17, 'd': 'dblp', 'n': 'MODELS'}, {'i': 'conf/cp', 'score': 15, 'd': 'dblp', 'n': 'CP'}, {'i': 'conf/hotos', 'score': 13, 'd': 'dblp', 'n': 'HOTOS'}, {'i': 'conf/lctrts', 'score': 13, 'd': 'dblp', 'n': 'LCTES'}, {'i': 'conf/etaps', 'score': 4, 'd': 'dblp', 'n': 'ETAPS'}, {'i': 'conf/fm', 'score': 1, 'd': 'dblp', 'n': 'FM'}, {'i': 'journals/tse', 'score': 168, 'd': 'dblp', 'n': 'ITSE'}, {'i': 'journals/tosem', 'score': 144, 'd': 'dblp', 'n': 'TOSEM'}, {'i': 'journals/toplas', 'score': 142, 'd': 'dblp', 'n': 'TOPLAS'}, {'i': 'journals/jss', 'score': 53, 'd': 'dblp', 'n': 'JSS'}, {'i': 'journals/infsof', 'score': 36, 'd': 'dblp', 'n': 'INFSOF'}, {'i': 'journals/tsc', 'score': 33, 'd': 'dblp', 'n': 'TSC'}, {'i': 'journals/ase', 'score': 30, 'd': 'dblp', 'n': 'ASE'}, {'i': 'journals/ese', 'score': 26, 'd': 'dblp', 'n': 'ESE'}, {'i': 'journals/scp', 'score': 26, 'd': 'dblp', 'n': 'SCP'}, {'i': 'journals/sosym', 'score': 23, 'd': 'dblp', 'n': 'SOSYM'}, {'i': 'journals/spe', 'score': 23, 'd': 'dblp', 'n': 'SPE'}, {'i': 'journals/stvr', 'score': 16, 'd': 'dblp', 'n': 'STVR'}, {'i': 'journals/jfp', 'score': 14, 'd': 'dblp', 'n': 'JFP'}, {'i': 'journals/smr', 'score': 12, 'd': 'dblp', 'n': 'SMR'}, {'i': 'journals/iee', 'score': 11, 'd': 'dblp', 'n': 'IETS'}, {'i': 'journals/re', 'score': 4, 'd': 'dblp', 'n': 'RE'}] ,"5": [{'i': 'conf/sigmod', 'score': 185, 'd': 'dblp', 'n': 'SIGMOD'}, {'i': 'conf/kdd', 'score': 176, 'd': 'dblp', 'n': 'KDD'}, {'i': 'conf/sigir', 'score': 167, 'd': 'dblp', 'n': 'SIGIR'}, {'i': 'conf/icde', 'score': 160, 'd': 'dblp', 'n': 'ICDE'}, {'i': 'conf/vldb', 'score': 147, 'd': 'dblp', 'n': 'VLDB'}, {'i': 'conf/wsdm', 'score': 50, 'd': 'dblp', 'n': 'WSDM'}, {'i': 'conf/cikm', 'score': 38, 'd': 'dblp', 'n': 'CIKM'}, {'i': 'conf/icdm', 'score': 33, 'd': 'dblp', 'n': 'ICDM'}, {'i': 'conf/edbt', 'score': 29, 'd': 'dblp', 'n': 'EDBT'}, {'i': 'conf/sdm', 'score': 29, 'd': 'dblp', 'n': 'SDM'}, {'i': 'conf/cidr', 'score': 23, 'd': 'dblp', 'n': 'CIDR'}, {'i': 'conf/pods', 'score': 23, 'd': 'dblp', 'n': 'PODS'}, {'i': 'conf/semweb', 'score': 18, 'd': 'dblp', 'n': 'ISWC'}, {'i': 'conf/ecml', 'score': 17, 'd': 'dblp', 'n': 'ECML'}, {'i': 'conf/icdt', 'score': 16, 'd': 'dblp', 'n': 'ICDT'}, {'i': 'conf/dasfaa', 'score': 6, 'd': 'dblp', 'n': 'DASFAA'}, {'i': 'journals/tkde', 'score': 173, 'd': 'dblp', 'n': 'TKDE'}, {'i': 'journals/vldb', 'score': 147, 'd': 'dblp', 'n': 'VLDB'}, {'i': 'journals/tods', 'score': 145, 'd': 'dblp', 'n': 'TODS'}, {'i': 'journals/tois', 'score': 139, 'd': 'dblp', 'n': 'TOIS'}, {'i': 'journals/isci', 'score': 62, 'd': 'dblp', 'n': 'ISCI'}, {'i': 'journals/datamine', 'score': 33, 'd': 'dblp', 'n': 'DMKD'}, {'i': 'journals/ws', 'score': 33, 'd': 'dblp', 'n': 'WS'}, {'i': 'journals/kais', 'score': 31, 'd': 'dblp', 'n': 'KAIS'}, {'i': 'journals/is', 'score': 28, 'd': 'dblp', 'n': 'IS'}, {'i': 'journals/aei', 'score': 26, 'd': 'dblp', 'n': 'AEI'}, {'i': 'journals/dke', 'score': 24, 'd': 'dblp', 'n': 'DKE'}, {'i': 'journals/ejis', 'score': 24, 'd': 'dblp', 'n': 'EJIS'}, {'i': 'journals/ipm', 'score': 24, 'd': 'dblp', 'n': 'IPM'}, {'i': 'journals/tkdd', 'score': 20, 'd': 'dblp', 'n': 'TKDD'}, {'i': 'journals/jasis', 'score': 19, 'd': 'dblp', 'n': 'JASIS'}, {'i': 'journals/tweb', 'score': 19, 'd': 'dblp', 'n': 'TWEB'}, {'i': 'journals/geoinformatica', 'score': 16, 'd': 'dblp', 'n': 'GEOINFORMATICA'}] ,"6": [{'i': 'conf/cav', 'score': 155, 'd': 'dblp', 'n': 'CAV'}, {'i': 'conf/focs', 'score': 151, 'd': 'dblp', 'n': 'FOCS'}, {'i': 'conf/stoc', 'score': 149, 'd': 'dblp', 'n': 'STOC'}, {'i': 'conf/lics', 'score': 138, 'd': 'dblp', 'n': 'LICS'}, {'i': 'conf/soda', 'score': 32, 'd': 'dblp', 'n': 'SODA'}, {'i': 'conf/hybrid', 'score': 22, 'd': 'dblp', 'n': 'HSCC'}, {'i': 'conf/concur', 'score': 21, 'd': 'dblp', 'n': 'CONCUR'}, {'i': 'conf/cade', 'score': 16, 'd': 'dblp', 'n': 'CADE'}, {'i': 'conf/compgeom', 'score': 16, 'd': 'dblp', 'n': 'SOCG'}, {'i': 'conf/icalp', 'score': 15, 'd': 'dblp', 'n': 'ICALP'}, {'i': 'conf/esa', 'score': 14, 'd': 'dblp', 'n': 'ESA'}, {'i': 'conf/coco', 'score': 13, 'd': 'dblp', 'n': 'CCC'}, {'i': 'journals/tit', 'score': 179, 'd': 'dblp', 'n': 'TIT'}, {'i': 'journals/siamcomp', 'score': 159, 'd': 'dblp', 'n': 'SICOMP'}, {'i': 'journals/iandc', 'score': 144, 'd': 'dblp', 'n': 'IANDC'}, {'i': 'journals/jcss', 'score': 32, 'd': 'dblp', 'n': 'JCSS'}, {'i': 'journals/talg', 'score': 30, 'd': 'dblp', 'n': 'TALG'}, {'i': 'journals/algorithmica', 'score': 27, 'd': 'dblp', 'n': 'ALGORITHMICA'}, {'i': 'journals/informs', 'score': 24, 'd': 'dblp', 'n': 'IJOC'}, {'i': 'journals/jgo', 'score': 22, 'd': 'dblp', 'n': 'JGO'}, {'i': 'journals/jsc', 'score': 19, 'd': 'dblp', 'n': 'JSC'}, {'i': 'journals/tocl', 'score': 19, 'd': 'dblp', 'n': 'TOCL'}, {'i': 'journals/toms', 'score': 18, 'd': 'dblp', 'n': 'TOMS'}, {'i': 'journals/fac', 'score': 17, 'd': 'dblp', 'n': 'FAC'}, {'i': 'journals/fmsd', 'score': 17, 'd': 'dblp', 'n': 'FMSD'}, {'i': 'journals/tcs', 'score': 15, 'd': 'dblp', 'n': 'TCS'}, {'i': 'journals/cc', 'score': 13, 'd': 'dblp', 'n': 'CC'}, {'i': 'journals/mscs', 'score': 13, 'd': 'dblp', 'n': 'MSCS'}] ,"7": [{'i': 'conf/mm', 'score': 157, 'd': 'dblp', 'n': 'MM'}, {'i': 'conf/vr', 'score': 138, 'd': 'dblp', 'n': 'VR'}, {'i': 'conf/visualization', 'score': 131, 'd': 'dblp', 'n': 'VISUALIZATION'}, {'i': 'conf/siggraph', 'score': 124, 'd': 'dblp', 'n': 'SIGGRAPH'}, {'i': 'conf/icassp', 'score': 45, 'd': 'dblp', 'n': 'ICASSP'}, {'i': 'conf/icmcs', 'score': 25, 'd': 'dblp', 'n': 'ICMCS'}, {'i': 'conf/si3d', 'score': 20, 'd': 'dblp', 'n': 'SI3D'}, {'i': 'conf/mir', 'score': 19, 'd': 'dblp', 'n': 'ICMR'}, {'i': 'conf/sca', 'score': 19, 'd': 'dblp', 'n': 'SCA'}, {'i': 'conf/dcc', 'score': 12, 'd': 'dblp', 'n': 'DCC'}, {'i': 'conf/eurographics', 'score': 7, 'd': 'dblp', 'n': 'EG'}, {'i': 'conf/sma', 'score': 6, 'd': 'dblp', 'n': 'SPM'}, {'i': 'conf/pg', 'score': 0, 'd': 'dblp', 'n': 'PG'}, {'i': 'conf/rt', 'score': 0, 'd': 'dblp', 'n': 'RT'}, {'i': 'conf/sgp', 'score': 0, 'd': 'dblp', 'n': 'SGP'}, {'i': 'conf/vissym', 'score': 0, 'd': 'dblp', 'n': 'VISSYM'}, {'i': 'journals/tip', 'score': 189, 'd': 'dblp', 'n': 'TIP'}, {'i': 'journals/tog', 'score': 181, 'd': 'dblp', 'n': 'TOG'}, {'i': 'journals/tvcg', 'score': 166, 'd': 'dblp', 'n': 'TVCG'}, {'i': 'journals/cgf', 'score': 41, 'd': 'dblp', 'n': 'CGF'}, {'i': 'journals/tcsv', 'score': 40, 'd': 'dblp', 'n': 'TCSV'}, {'i': 'journals/tmm', 'score': 40, 'd': 'dblp', 'n': 'TMM'}, {'i': 'journals/siamis', 'score': 32, 'd': 'dblp', 'n': 'SIAMIS'}, {'i': 'journals/speech', 'score': 28, 'd': 'dblp', 'n': 'SPEECH'}, {'i': 'journals/cad', 'score': 25, 'd': 'dblp', 'n': 'CAD'}, {'i': 'journals/tomccap', 'score': 20, 'd': 'dblp', 'n': 'TOMCCAP'}, {'i': 'journals/cagd', 'score': 15, 'd': 'dblp', 'n': 'CAGD'}, {'i': 'journals/cvgip', 'score': 11, 'd': 'dblp', 'n': 'GM'}] ,"8": [{'i': 'conf/cvpr', 'score': 232, 'd': 'dblp', 'n': 'CVPR'}, {'i': 'conf/iccv', 'score': 178, 'd': 'dblp', 'n': 'ICCV'}, {'i': 'conf/icml', 'score': 176, 'd': 'dblp', 'n': 'ICML'}, {'i': 'conf/nips', 'score': 171, 'd': 'dblp', 'n': 'NIPS'}, {'i': 'conf/acl', 'score': 168, 'd': 'dblp', 'n': 'ACL'}, {'i': 'conf/aaai', 'score': 164, 'd': 'dblp', 'n': 'AAAI'}, {'i': 'conf/ijcai', 'score': 155, 'd': 'dblp', 'n': 'IJCAI'}, {'i': 'conf/par', 'score': 67, 'd': 'dblp', 'n': 'PAR'}, {'i': 'conf/icra', 'score': 58, 'd': 'dblp', 'n': 'ICRA'}, {'i': 'conf/emnlp', 'score': 45, 'd': 'dblp', 'n': 'EMNLP'}, {'i': 'conf/coling', 'score': 26, 'd': 'dblp', 'n': 'COLING'}, {'i': 'conf/kr', 'score': 24, 'd': 'dblp', 'n': 'KR'}, {'i': 'conf/atal', 'score': 23, 'd': 'dblp', 'n': 'ATAL'}, {'i': 'conf/aips', 'score': 20, 'd': 'dblp', 'n': 'ICAPS'}, {'i': 'conf/colt', 'score': 20, 'd': 'dblp', 'n': 'COLT'}, {'i': 'conf/ecai', 'score': 20, 'd': 'dblp', 'n': 'ECAI'}, {'i': 'conf/eccv', 'score': 16, 'd': 'dblp', 'n': 'ECCV'}, {'i': 'conf/ppsn', 'score': 15, 'd': 'dblp', 'n': 'PPSN'}, {'i': 'conf/uai', 'score': 15, 'd': 'dblp', 'n': 'UAI'}, {'i': 'conf/iccbr', 'score': 10, 'd': 'dblp', 'n': 'ICCBR'}, {'i': 'journals/pami', 'score': 234, 'd': 'dblp', 'n': 'PAMI'}, {'i': 'journals/ijcv', 'score': 178, 'd': 'dblp', 'n': 'IJCV'}, {'i': 'journals/jmlr', 'score': 169, 'd': 'dblp', 'n': 'JMLR'}, {'i': 'journals/ai', 'score': 168, 'd': 'dblp', 'n': 'AI'}, {'i': 'journals/taslp', 'score': 46, 'd': 'dblp', 'n': 'TASLP'}, {'i': 'journals/tfs', 'score': 44, 'd': 'dblp', 'n': 'TFS'}, {'i': 'journals/tec', 'score': 38, 'd': 'dblp', 'n': 'TEVC'}, {'i': 'journals/cviu', 'score': 34, 'd': 'dblp', 'n': 'CVIU'}, {'i': 'journals/ml', 'score': 33, 'd': 'dblp', 'n': 'ML'}, {'i': 'journals/nn', 'score': 32, 'd': 'dblp', 'n': 'NN'}, {'i': 'journals/ijar', 'score': 31, 'd': 'dblp', 'n': 'IJAR'}, {'i': 'journals/tnn', 'score': 31, 'd': 'dblp', 'n': 'TNNLS'}, {'i': 'journals/neco', 'score': 30, 'd': 'dblp', 'n': 'NC'}, {'i': 'journals/ec', 'score': 27, 'd': 'dblp', 'n': 'EC'}, {'i': 'journals/coling', 'score': 26, 'd': 'dblp', 'n': 'COLING'}, {'i': 'journals/jair', 'score': 26, 'd': 'dblp', 'n': 'JAIR'}, {'i': 'journals/taffco', 'score': 26, 'd': 'dblp', 'n': 'TAC'}, {'i': 'journals/aamas', 'score': 23, 'd': 'dblp', 'n': 'AAMAS'}, {'i': 'journals/jar', 'score': 20, 'd': 'dblp', 'n': 'JAR'}, {'i': 'journals/tap', 'score': 16, 'd': 'dblp', 'n': 'TAP'}, {'i': 'journals/tslp', 'score': 9, 'd': 'dblp', 'n': 'TSLP'}, {'i': 'journals/tcyb', 'score': 6, 'd': 'dblp', 'n': 'TCYB'}] ,"9": [{'i': 'conf/chi', 'score': 191, 'd': 'dblp', 'n': 'CHI'}, {'i': 'conf/cscw', 'score': 160, 'd': 'dblp', 'n': 'CSCW'}, {'i': 'conf/huc', 'score': 149, 'd': 'dblp', 'n': 'HUC'}, {'i': 'conf/uist', 'score': 39, 'd': 'dblp', 'n': 'UIST'}, {'i': 'conf/percom', 'score': 28, 'd': 'dblp', 'n': 'PERCOM'}, {'i': 'conf/mhci', 'score': 27, 'd': 'dblp', 'n': 'MHCI'}, {'i': 'conf/iui', 'score': 21, 'd': 'dblp', 'n': 'IUI'}, {'i': 'conf/tabletop', 'score': 20, 'd': 'dblp', 'n': 'TABLETOP'}, {'i': 'conf/group', 'score': 12, 'd': 'dblp', 'n': 'GROUP'}, {'i': 'conf/ecscw', 'score': 0, 'd': 'dblp', 'n': 'ECSCW'}, {'i': 'journals/ijmms', 'score': 147, 'd': 'dblp', 'n': 'IJHCS'}, {'i': 'journals/tochi', 'score': 140, 'd': 'dblp', 'n': 'TOCHI'}, {'i': 'journals/iwc', 'score': 24, 'd': 'dblp', 'n': 'IWC'}, {'i': 'journals/umuai', 'score': 23, 'd': 'dblp', 'n': 'UMUAI'}, {'i': 'journals/cscw', 'score': 17, 'd': 'dblp', 'n': 'CSCW'}, {'i': 'journals/ijhci', 'score': 17, 'd': 'dblp', 'n': 'IJHCI'}, {'i': 'journals/thms', 'score': 15, 'd': 'dblp', 'n': 'THMS'}, {'i': 'journals/hhci', 'score': 14, 'd': 'dblp', 'n': 'HCI'}] ,"10": [{'i': 'conf/www', 'score': 186, 'd': 'dblp', 'n': 'WWW'}, {'i': 'conf/rtss', 'score': 144, 'd': 'dblp', 'n': 'RTSS'}, {'i': 'conf/cogsci', 'score': 31, 'd': 'dblp', 'n': 'COGSCI'}, {'i': 'conf/recomb', 'score': 18, 'd': 'dblp', 'n': 'RECOMB'}, {'i': 'conf/emsoft', 'score': 17, 'd': 'dblp', 'n': 'EMSOFT'}, {'i': 'conf/bibm', 'score': 13, 'd': 'dblp', 'n': 'BIBM'}, {'i': 'journals/pieee', 'score': 184, 'd': 'dblp', 'n': 'PIEEE'}, {'i': 'journals/jacm', 'score': 150, 'd': 'dblp', 'n': 'JACM'}, {'i': 'journals/bioinformatics', 'score': 79, 'd': 'dblp', 'n': 'BIOINFORMATICS'}, {'i': 'journals/ploscb', 'score': 61, 'd': 'dblp', 'n': 'PLOSCB'}, {'i': 'journals/tgrs', 'score': 55, 'd': 'dblp', 'n': 'TGRS'}, {'i': 'journals/tmi', 'score': 53, 'd': 'dblp', 'n': 'TMI'}, {'i': 'journals/trob', 'score': 45, 'd': 'dblp', 'n': 'TR'}, {'i': 'journals/tits', 'score': 41, 'd': 'dblp', 'n': 'TITS'}, {'i': 'journals/jamia', 'score': 37, 'd': 'dblp', 'n': 'JAMIA'}, {'i': 'journals/bib', 'score': 35, 'd': 'dblp', 'n': 'BIB'}, {'i': 'journals/tase', 'score': 31, 'd': 'dblp', 'n': 'TASE'}, {'i': 'journals/wwwj', 'score': 23, 'd': 'dblp', 'n': 'WWWJ'}, {'i': 'journals/cj', 'score': 22, 'd': 'dblp', 'n': 'CJ'}, {'i': 'journals/jcst', 'score': 14, 'd': 'dblp', 'n': 'JCST'}, {'i': 'journals/chinaf', 'score': 13, 'd': 'dblp', 'n': 'CHINAF'}],"11":[{"i": "chemistry", "d": "doaj","n":"DOAJ"}],"12":[{"i": "civil", "d": "doaj","n":"DOAJ"}],"13":[{"i": "education", "d": "doaj","n":"DOAJ"}],"14":[{"i": "electrical", "d": "doaj","n":"DOAJ"}],"15":[{"i": "geology", "d": "doaj","n":"DOAJ"}],"16":[{"i": "mathematics", "d": "doaj","n":"DOAJ"},{"i": "mathematics", "d": "arxiv","n":"ARXIV"}],"17":[{"i": "physics", "d": "doaj","n":"DOAJ"},{"i": "physics", "d": "arxiv","n":"ARXIV"}],"18":[{"i": "psychology", "d": "doaj","n":"DOAJ"}],"19":[{"i": "qfin", "d": "arxiv","n":"ARXIV"}],"20":[{"i": "statistics", "d": "arxiv","n":"ARXIV"}]}
CORPUS2ID=[]
FIELD_NAME = [u'通用语料库',u'计算机', u"化学",u"土木",u"教育",u"电子",u"地质",u"数学",u"物理",u"心理",u"金融工程",u"统计"]
SECOND_LEVEL_FIELD=[[u'BNC'],[u'高性能计算', u'计算机网络', u'网络安全', u'软件工程', u'数据挖掘',
              u'计算机理论', u'计算机图形学', u'人工智能', u'人机交互',  u'交叉综合'],[u"化学"],[u"土木"],[u"教育"],[u"电子"],[u"地质"],[u"数学"],[u"物理"],[u"心理"],[u"金融工程"],[u"统计"]]
count=0
count1=0
for i in range(21):
    if count==0:
        count=len(SECOND_LEVEL_FIELD[count1])
        count1+=1
        CORPUS2ID.append("")
    CORPUS2ID.append("")
    count-=1
    for j in CORPUS[str(i)]:
        CORPUS2ID.append(j)

def refine_query(q):
    # Note the difference between str.translate and unicode.translate
    r = q.translate(TRANS_TABLE).strip()
    r = re.sub(' +', ' ', r)
    if r != q:
        logger.info('refine_query: "%s" -> %s', q, r)
    return r

def convert_type2title(rr):
    rr_title = ''
    if '*' in rr:
        rr_title = re.sub('[a-zA-Z]*', '', rr).strip()
        rr_title = rr.replace(rr_title, DEPS_VIEW[rr_title])
    return rr_title if rr_title else rr


def debug_object(o):
    print '<---- object -----'
    print '\n'.join(["%s:%s" % item for item in o.__dict__.items()])
    print '----- object ---->'


def is_cn_char(c):
    return 0x4e00 <= ord(c) < 0x9fa6


def has_cn(s):
    return reduce(lambda x, y: x or y, [is_cn_char(c) for c in s], False)


def corpus_id2cids(corpus_id):
    dbs, cids = set(), set()
    for i in range(0,len(corpus_id)):
        if corpus_id[i]!=0:
            if CORPUS2ID[i]!="":
                dbs.add(CORPUS2ID[i]['d'])
                cids.add(CORPUS2ID[i]["i"].replace('/', '_'))
    return list(dbs), list(cids)


def notstar(p, q):
    return p if p != '*' else q


def cleaned_sentence(s):
	# eliminate all possibility of bad HTML in sentence to mark as safe
	return s.replace('<', '< ').replace('< strong>', '<strong>').replace('< /strong>', '</strong>')

def generate_source(year, title, authList, conference):
    source = ''
    # assert: should always be this case
    conference += "'" + str(year % 100)
    source += conference + '. '

    if authList:
        nameList = authList[0].split()  # split first author's name
        authorShort = nameList[0][0].upper() + '. ' +nameList[len(nameList) - 1]
        if len(authList) > 1:
            authorShort += ' et. al.'
        else:
            authorShort += '.'
        source += authorShort
    source += ' ' + title
    return source


def gen_source_url(p):
    year = int(p.get('year'))
    title = p.get('title', '')
    authList = p.get('authors', '').split(';')
    conference = p.get('venue', '/').split('/')[-1].upper()
    source = generate_source(year, title, authList, conference)
    return {'source': source, 'url': p['ee']}


def papers_source_str(pids):
    p = mongo_get_objects(DblpPaper, pks=pids)
    if not p:
        return {}
    # TODO: precompute source string and save to $common.uploads
    # venues = [i['venue'] for i in p.values()]
    # v = mongo_get_objects(DblpVenue, pks=venues)

    res = {}
    for i in pids:
        if i in p:
            res[i] = gen_source_url(p[i])
    return res

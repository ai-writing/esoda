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


CORPUS = {"0": [{"i": "bnc", "d": "bnc",'n':"BNC"}], "1": [{'i': 'journals/tpds', 'h5': 55, 'd': 'dblp', 'n': 'TPDS'}, {'i': 'conf/sc', 'h5': 39, 'd': 'dblp', 'n': 'SC'}, {'i': 'conf/asplos', 'h5': 38, 'd': 'dblp', 'n': 'ASPLOS'}, {'i': 'conf/cloud', 'h5': 38, 'd': 'dblp', 'n': 'SOCC'}, {'i': 'conf/eurosys', 'h5': 37, 'd': 'dblp', 'n': 'EUROSYS'}, {'i': 'conf/icdcs', 'h5': 36, 'd': 'dblp', 'n': 'ICDCS'}, {'i': 'conf/isca', 'h5': 36, 'd': 'dblp', 'n': 'ISCA'}, {'i': 'journals/tc', 'h5': 36, 'd': 'dblp', 'n': 'TOC'}, {'i': 'conf/date', 'h5': 35, 'd': 'dblp', 'n': 'DATE'}, {'i': 'journals/tvlsi', 'h5': 35, 'd': 'dblp', 'n': 'TVLSI'}, {'i': 'conf/cnhpca', 'h5': 34, 'd': 'dblp', 'n': 'HPCA'}, {'i': 'conf/ipps', 'h5': 34, 'd': 'dblp', 'n': 'IPDPS'}, {'i': 'conf/eurodac', 'h5': 33, 'd': 'dblp', 'n': 'DAC'}, {'i': 'journals/micro', 'h5': 32, 'd': 'dblp', 'n': 'MICRO'}, {'i': 'conf/hpdc', 'h5': 30, 'd': 'dblp', 'n': 'HPDC'}, {'i': 'journals/jpdc', 'h5': 30, 'd': 'dblp', 'n': 'JPDC'}, {'i': 'journals/tcad', 'h5': 30, 'd': 'dblp', 'n': 'TCAD'}, {'i': 'conf/IEEEpact', 'h5': 28, 'd': 'dblp', 'n': 'PACT'}, {'i': 'conf/fast', 'h5': 28, 'd': 'dblp', 'n': 'FAST'}, {'i': 'conf/sigmetrics', 'h5': 26, 'd': 'dblp', 'n': 'SIGMETRICS'}, {'i': 'conf/cgo', 'h5': 23, 'd': 'dblp', 'n': 'CGO'}, {'i': 'conf/ics', 'h5': 23, 'd': 'dblp', 'n': 'ICS'}, {'i': 'conf/ppopp', 'h5': 23, 'd': 'dblp', 'n': 'PPOPP'}, {'i': 'conf/iccad', 'h5': 21, 'd': 'dblp', 'n': 'ICCAD'}, {'i': 'journals/jsa', 'h5': 21, 'd': 'dblp', 'n': 'JSA'}, {'i': 'journals/pe', 'h5': 21, 'd': 'dblp', 'n': 'PE'}, {'i': 'conf/podc', 'h5': 20, 'd': 'dblp', 'n': 'PODC'}, {'i': 'conf/spaa', 'h5': 20, 'd': 'dblp', 'n': 'SPAA'}, {'i': 'journals/tecs', 'h5': 20, 'd': 'dblp', 'n': 'TECS'}, {'i': 'conf/codes', 'h5': 19, 'd': 'dblp', 'n': 'CODES'}, {'i': 'conf/fpga', 'h5': 19, 'd': 'dblp', 'n': 'FPGA'}, {'i': 'conf/icpp', 'h5': 19, 'd': 'dblp', 'n': 'ICPP'}, {'i': 'conf/vee', 'h5': 19, 'd': 'dblp', 'n': 'VEE'}, {'i': 'journals/tos', 'h5': 19, 'd': 'dblp', 'n': 'TOS'}, {'i': 'journals/taco', 'h5': 18, 'd': 'dblp', 'n': 'TACO'}, {'i': 'journals/tocs', 'h5': 18, 'd': 'dblp', 'n': 'TOCS'}, {'i': 'conf/mss', 'h5': 16, 'd': 'dblp', 'n': 'MSST'}, {'i': 'conf/itc', 'h5': 15, 'd': 'dblp', 'n': 'ITC'}, {'i': 'conf/hipeac', 'h5': 14, 'd': 'dblp', 'n': 'HIPC'}, {'i': 'journals/taas', 'h5': 14, 'd': 'dblp', 'n': 'TAAS'}, {'i': 'journals/todaes', 'h5': 14, 'd': 'dblp', 'n': 'TODAES'}, {'i': 'journals/trets', 'h5': 13, 'd': 'dblp', 'n': 'TRETS'}, {'i': 'conf/iccd', 'h5': 12, 'd': 'dblp', 'n': 'ICCD'}, {'i': 'conf/lisa', 'h5': 10, 'd': 'dblp', 'n': 'LISA'}, {'i': 'conf/parco', 'h5': 7, 'd': 'dblp', 'n': 'PARCO'}, {'i': 'conf/usenix', 'h5': 7, 'd': 'dblp', 'n': 'USENIX'}, {'i': 'conf/rtas', 'h5': 3, 'd': 'dblp', 'n': 'RTAS'}, {'i': 'conf/performance', 'h5': 0, 'd': 'dblp', 'n': 'PERFORMANCE'}] ,"2": [{'i': 'conf/infocom', 'h5': 69, 'd': 'dblp', 'n': 'INFOCOM'}, {'i': 'journals/twc', 'h5': 61, 'd': 'dblp', 'n': 'TWC'}, {'i': 'journals/ton', 'h5': 55, 'd': 'dblp', 'n': 'TON'}, {'i': 'journals/tmc', 'h5': 53, 'd': 'dblp', 'n': 'TMC'}, {'i': 'conf/nsdi', 'h5': 52, 'd': 'dblp', 'n': 'NSDI'}, {'i': 'journals/jsac', 'h5': 51, 'd': 'dblp', 'n': 'JSAC'}, {'i': 'conf/sigcomm', 'h5': 49, 'd': 'dblp', 'n': 'SIGCOMM'}, {'i': 'journals/tcom', 'h5': 46, 'd': 'dblp', 'n': 'TOC'}, {'i': 'conf/imc', 'h5': 41, 'd': 'dblp', 'n': 'IMC'}, {'i': 'conf/mobisys', 'h5': 40, 'd': 'dblp', 'n': 'MOBISYS'}, {'i': 'journals/cn', 'h5': 39, 'd': 'dblp', 'n': 'CN'}, {'i': 'conf/mobicom', 'h5': 37, 'd': 'dblp', 'n': 'MOBICOM'}, {'i': 'conf/sensys', 'h5': 33, 'd': 'dblp', 'n': 'SENSYS'}, {'i': 'conf/ipsn', 'h5': 30, 'd': 'dblp', 'n': 'IPSN'}, {'i': 'conf/conext', 'h5': 28, 'd': 'dblp', 'n': 'CONEXT'}, {'i': 'journals/tosn', 'h5': 28, 'd': 'dblp', 'n': 'TOSN'}, {'i': 'conf/mobihoc', 'h5': 23, 'd': 'dblp', 'n': 'MOBIHOC'}, {'i': 'conf/icnp', 'h5': 21, 'd': 'dblp', 'n': 'ICNP'}, {'i': 'conf/iwqos', 'h5': 16, 'd': 'dblp', 'n': 'IWQOS'}, {'i': 'conf/secon', 'h5': 15, 'd': 'dblp', 'n': 'SECON'}, {'i': 'conf/nossdav', 'h5': 14, 'd': 'dblp', 'n': 'NOSSDAV'}, {'i': 'journals/toit', 'h5': 12, 'd': 'dblp', 'n': 'TOIT'}] ,"3": [{'i': 'conf/sp', 'h5': 49, 'd': 'dblp', 'n': 'SP'}, {'i': 'conf/ccs', 'h5': 44, 'd': 'dblp', 'n': 'CCS'}, {'i': 'journals/tifs', 'h5': 43, 'd': 'dblp', 'n': 'TIFS'}, {'i': 'conf/uss', 'h5': 41, 'd': 'dblp', 'n': 'USS'}, {'i': 'conf/ndss', 'h5': 36, 'd': 'dblp', 'n': 'NDSS'}, {'i': 'journals/tdsc', 'h5': 31, 'd': 'dblp', 'n': 'TDSC'}, {'i': 'conf/eurocrypt', 'h5': 30, 'd': 'dblp', 'n': 'EUROCRYPT'}, {'i': 'conf/acsac', 'h5': 29, 'd': 'dblp', 'n': 'ACSAC'}, {'i': 'journals/compsec', 'h5': 27, 'd': 'dblp', 'n': 'COMPSEC'}, {'i': 'conf/ches', 'h5': 26, 'd': 'dblp', 'n': 'CHES'}, {'i': 'conf/crypto', 'h5': 24, 'd': 'dblp', 'n': 'CRYPTO'}, {'i': 'journals/joc', 'h5': 23, 'd': 'dblp', 'n': 'JOC'}, {'i': 'journals/tissec', 'h5': 23, 'd': 'dblp', 'n': 'TISS'}, {'i': 'conf/asiacrypt', 'h5': 22, 'd': 'dblp', 'n': 'ASIACRYPT'}, {'i': 'conf/csfw', 'h5': 22, 'd': 'dblp', 'n': 'CSFW'}, {'i': 'conf/dsn', 'h5': 21, 'd': 'dblp', 'n': 'DSN'}, {'i': 'conf/pkc', 'h5': 21, 'd': 'dblp', 'n': 'PKC'}, {'i': 'journals/jcs', 'h5': 21, 'd': 'dblp', 'n': 'JCS'}, {'i': 'conf/esorics', 'h5': 20, 'd': 'dblp', 'n': 'ESORICS'}, {'i': 'conf/raid', 'h5': 20, 'd': 'dblp', 'n': 'RAID'}, {'i': 'conf/tcc', 'h5': 19, 'd': 'dblp', 'n': 'TCC'}, {'i': 'conf/fse', 'h5': 18, 'd': 'dblp', 'n': 'FSE'}, {'i': 'conf/srds', 'h5': 16, 'd': 'dblp', 'n': 'SRDS'}, {'i': 'journals/dcc', 'h5': 14, 'd': 'dblp', 'n': 'DCC'}] ,"4": [{'i': 'journals/jss', 'h5': 53, 'd': 'dblp', 'n': 'JSS'}, {'i': 'journals/tse', 'h5': 48, 'd': 'dblp', 'n': 'ITSE'}, {'i': 'conf/icse', 'h5': 43, 'd': 'dblp', 'n': 'ICSE'}, {'i': 'conf/pldi', 'h5': 36, 'd': 'dblp', 'n': 'PLDI'}, {'i': 'conf/popl', 'h5': 36, 'd': 'dblp', 'n': 'POPL'}, {'i': 'journals/infsof', 'h5': 36, 'd': 'dblp', 'n': 'INFSOF'}, {'i': 'conf/osdi', 'h5': 33, 'd': 'dblp', 'n': 'OSDI'}, {'i': 'journals/tsc', 'h5': 33, 'd': 'dblp', 'n': 'TSC'}, {'i': 'conf/kbse', 'h5': 30, 'd': 'dblp', 'n': 'ASE'}, {'i': 'journals/ase', 'h5': 30, 'd': 'dblp', 'n': 'ASE'}, {'i': 'conf/oopsla', 'h5': 28, 'd': 'dblp', 'n': 'OOPSLA'}, {'i': 'conf/icws', 'h5': 26, 'd': 'dblp', 'n': 'ICWS'}, {'i': 'journals/ese', 'h5': 26, 'd': 'dblp', 'n': 'ESE'}, {'i': 'journals/scp', 'h5': 26, 'd': 'dblp', 'n': 'SCP'}, {'i': 'conf/issta', 'h5': 25, 'd': 'dblp', 'n': 'ISSTA'}, {'i': 'conf/sosp', 'h5': 25, 'd': 'dblp', 'n': 'SOSP'}, {'i': 'conf/ecoop', 'h5': 24, 'd': 'dblp', 'n': 'ECOOP'}, {'i': 'conf/icsm', 'h5': 24, 'd': 'dblp', 'n': 'ICSM'}, {'i': 'journals/tosem', 'h5': 24, 'd': 'dblp', 'n': 'TOSEM'}, {'i': 'journals/sosym', 'h5': 23, 'd': 'dblp', 'n': 'SOSYM'}, {'i': 'journals/spe', 'h5': 23, 'd': 'dblp', 'n': 'SPE'}, {'i': 'journals/toplas', 'h5': 22, 'd': 'dblp', 'n': 'TOPLAS'}, {'i': 'conf/icfp', 'h5': 21, 'd': 'dblp', 'n': 'ICFP'}, {'i': 'conf/icsoc', 'h5': 21, 'd': 'dblp', 'n': 'ICSOC'}, {'i': 'conf/re', 'h5': 21, 'd': 'dblp', 'n': 'RE'}, {'i': 'conf/iwpc', 'h5': 20, 'd': 'dblp', 'n': 'ICPC'}, {'i': 'conf/middleware', 'h5': 19, 'd': 'dblp', 'n': 'MIDDLEWARE'}, {'i': 'conf/caise', 'h5': 18, 'd': 'dblp', 'n': 'CAISE'}, {'i': 'conf/esem', 'h5': 18, 'd': 'dblp', 'n': 'ESEM'}, {'i': 'conf/issre', 'h5': 18, 'd': 'dblp', 'n': 'ISSRE'}, {'i': 'conf/sas', 'h5': 18, 'd': 'dblp', 'n': 'SAS'}, {'i': 'conf/vmcai', 'h5': 18, 'd': 'dblp', 'n': 'VMCAI'}, {'i': 'conf/wcre', 'h5': 18, 'd': 'dblp', 'n': 'WCRE'}, {'i': 'conf/models', 'h5': 17, 'd': 'dblp', 'n': 'MODELS'}, {'i': 'journals/stvr', 'h5': 16, 'd': 'dblp', 'n': 'STVR'}, {'i': 'conf/cp', 'h5': 15, 'd': 'dblp', 'n': 'CP'}, {'i': 'journals/jfp', 'h5': 14, 'd': 'dblp', 'n': 'JFP'}, {'i': 'conf/hotos', 'h5': 13, 'd': 'dblp', 'n': 'HOTOS'}, {'i': 'conf/lctrts', 'h5': 13, 'd': 'dblp', 'n': 'LCTES'}, {'i': 'journals/smr', 'h5': 12, 'd': 'dblp', 'n': 'SMR'}, {'i': 'journals/iee', 'h5': 11, 'd': 'dblp', 'n': 'IETS'}, {'i': 'conf/etaps', 'h5': 4, 'd': 'dblp', 'n': 'ETAPS'}, {'i': 'journals/re', 'h5': 4, 'd': 'dblp', 'n': 'RE'}, {'i': 'conf/fm', 'h5': 1, 'd': 'dblp', 'n': 'FM'}, {'i': 'conf/sigsoft', 'h5': 0, 'd': 'dblp', 'n': 'ESEC'}] ,"5": [{'i': 'conf/sigmod', 'h5': 65, 'd': 'dblp', 'n': 'SIGMOD'}, {'i': 'journals/isci', 'h5': 62, 'd': 'dblp', 'n': 'ISCI'}, {'i': 'conf/kdd', 'h5': 56, 'd': 'dblp', 'n': 'KDD'}, {'i': 'journals/tkde', 'h5': 53, 'd': 'dblp', 'n': 'TKDE'}, {'i': 'conf/wsdm', 'h5': 50, 'd': 'dblp', 'n': 'WSDM'}, {'i': 'conf/sigir', 'h5': 47, 'd': 'dblp', 'n': 'SIGIR'}, {'i': 'conf/icde', 'h5': 40, 'd': 'dblp', 'n': 'ICDE'}, {'i': 'conf/cikm', 'h5': 38, 'd': 'dblp', 'n': 'CIKM'}, {'i': 'conf/icdm', 'h5': 33, 'd': 'dblp', 'n': 'ICDM'}, {'i': 'journals/datamine', 'h5': 33, 'd': 'dblp', 'n': 'DMKD'}, {'i': 'journals/ws', 'h5': 33, 'd': 'dblp', 'n': 'WS'}, {'i': 'journals/kais', 'h5': 31, 'd': 'dblp', 'n': 'KAIS'}, {'i': 'conf/edbt', 'h5': 29, 'd': 'dblp', 'n': 'EDBT'}, {'i': 'conf/sdm', 'h5': 29, 'd': 'dblp', 'n': 'SDM'}, {'i': 'journals/is', 'h5': 28, 'd': 'dblp', 'n': 'IS'}, {'i': 'conf/vldb', 'h5': 27, 'd': 'dblp', 'n': 'VLDB'}, {'i': 'journals/vldb', 'h5': 27, 'd': 'dblp', 'n': 'VLDB'}, {'i': 'journals/aei', 'h5': 26, 'd': 'dblp', 'n': 'AEI'}, {'i': 'journals/tods', 'h5': 25, 'd': 'dblp', 'n': 'TODS'}, {'i': 'journals/dke', 'h5': 24, 'd': 'dblp', 'n': 'DKE'}, {'i': 'journals/ejis', 'h5': 24, 'd': 'dblp', 'n': 'EJIS'}, {'i': 'journals/ipm', 'h5': 24, 'd': 'dblp', 'n': 'IPM'}, {'i': 'conf/cidr', 'h5': 23, 'd': 'dblp', 'n': 'CIDR'}, {'i': 'conf/pods', 'h5': 23, 'd': 'dblp', 'n': 'PODS'}, {'i': 'journals/tkdd', 'h5': 20, 'd': 'dblp', 'n': 'TKDD'}, {'i': 'journals/jasis', 'h5': 19, 'd': 'dblp', 'n': 'JASIS'}, {'i': 'journals/tois', 'h5': 19, 'd': 'dblp', 'n': 'TOIS'}, {'i': 'journals/tweb', 'h5': 19, 'd': 'dblp', 'n': 'TWEB'}, {'i': 'conf/semweb', 'h5': 18, 'd': 'dblp', 'n': 'ISWC'}, {'i': 'conf/ecml', 'h5': 17, 'd': 'dblp', 'n': 'ECML'}, {'i': 'conf/icdt', 'h5': 16, 'd': 'dblp', 'n': 'ICDT'}, {'i': 'journals/geoinformatica', 'h5': 16, 'd': 'dblp', 'n': 'GEOINFORMATICA'}, {'i': 'conf/dasfaa', 'h5': 6, 'd': 'dblp', 'n': 'DASFAA'}] ,"6": [{'i': 'journals/tit', 'h5': 59, 'd': 'dblp', 'n': 'TIT'}, {'i': 'journals/siamcomp', 'h5': 39, 'd': 'dblp', 'n': 'SICOMP'}, {'i': 'conf/cav', 'h5': 35, 'd': 'dblp', 'n': 'CAV'}, {'i': 'conf/soda', 'h5': 32, 'd': 'dblp', 'n': 'SODA'}, {'i': 'journals/jcss', 'h5': 32, 'd': 'dblp', 'n': 'JCSS'}, {'i': 'conf/focs', 'h5': 31, 'd': 'dblp', 'n': 'FOCS'}, {'i': 'journals/talg', 'h5': 30, 'd': 'dblp', 'n': 'TALG'}, {'i': 'conf/stoc', 'h5': 29, 'd': 'dblp', 'n': 'STOC'}, {'i': 'journals/algorithmica', 'h5': 27, 'd': 'dblp', 'n': 'ALGORITHMICA'}, {'i': 'journals/iandc', 'h5': 24, 'd': 'dblp', 'n': 'IANDC'}, {'i': 'journals/informs', 'h5': 24, 'd': 'dblp', 'n': 'IJOC'}, {'i': 'conf/hybrid', 'h5': 22, 'd': 'dblp', 'n': 'HSCC'}, {'i': 'journals/jgo', 'h5': 22, 'd': 'dblp', 'n': 'JGO'}, {'i': 'conf/concur', 'h5': 21, 'd': 'dblp', 'n': 'CONCUR'}, {'i': 'journals/jsc', 'h5': 19, 'd': 'dblp', 'n': 'JSC'}, {'i': 'journals/tocl', 'h5': 19, 'd': 'dblp', 'n': 'TOCL'}, {'i': 'conf/lics', 'h5': 18, 'd': 'dblp', 'n': 'LICS'}, {'i': 'journals/toms', 'h5': 18, 'd': 'dblp', 'n': 'TOMS'}, {'i': 'journals/fac', 'h5': 17, 'd': 'dblp', 'n': 'FAC'}, {'i': 'journals/fmsd', 'h5': 17, 'd': 'dblp', 'n': 'FMSD'}, {'i': 'conf/cade', 'h5': 16, 'd': 'dblp', 'n': 'CADE'}, {'i': 'conf/compgeom', 'h5': 16, 'd': 'dblp', 'n': 'SOCG'}, {'i': 'conf/icalp', 'h5': 15, 'd': 'dblp', 'n': 'ICALP'}, {'i': 'journals/tcs', 'h5': 15, 'd': 'dblp', 'n': 'TCS'}, {'i': 'conf/esa', 'h5': 14, 'd': 'dblp', 'n': 'ESA'}, {'i': 'conf/coco', 'h5': 13, 'd': 'dblp', 'n': 'CCC'}, {'i': 'journals/cc', 'h5': 13, 'd': 'dblp', 'n': 'CC'}, {'i': 'journals/mscs', 'h5': 13, 'd': 'dblp', 'n': 'MSCS'}] ,"7": [{'i': 'journals/tip', 'h5': 69, 'd': 'dblp', 'n': 'TIP'}, {'i': 'journals/tog', 'h5': 61, 'd': 'dblp', 'n': 'TOG'}, {'i': 'journals/tvcg', 'h5': 46, 'd': 'dblp', 'n': 'TVCG'}, {'i': 'conf/icassp', 'h5': 45, 'd': 'dblp', 'n': 'ICASSP'}, {'i': 'journals/cgf', 'h5': 41, 'd': 'dblp', 'n': 'CGF'}, {'i': 'journals/tcsv', 'h5': 40, 'd': 'dblp', 'n': 'TCSV'}, {'i': 'journals/tmm', 'h5': 40, 'd': 'dblp', 'n': 'TMM'}, {'i': 'conf/mm', 'h5': 37, 'd': 'dblp', 'n': 'MM'}, {'i': 'journals/siamis', 'h5': 32, 'd': 'dblp', 'n': 'SIAMIS'}, {'i': 'journals/speech', 'h5': 28, 'd': 'dblp', 'n': 'SPEECH'}, {'i': 'conf/icmcs', 'h5': 25, 'd': 'dblp', 'n': 'ICMCS'}, {'i': 'journals/cad', 'h5': 25, 'd': 'dblp', 'n': 'CAD'}, {'i': 'conf/si3d', 'h5': 20, 'd': 'dblp', 'n': 'SI3D'}, {'i': 'journals/tomccap', 'h5': 20, 'd': 'dblp', 'n': 'TOMCCAP'}, {'i': 'conf/mir', 'h5': 19, 'd': 'dblp', 'n': 'ICMR'}, {'i': 'conf/sca', 'h5': 19, 'd': 'dblp', 'n': 'SCA'}, {'i': 'conf/vr', 'h5': 18, 'd': 'dblp', 'n': 'VR'}, {'i': 'journals/cagd', 'h5': 15, 'd': 'dblp', 'n': 'CAGD'}, {'i': 'conf/dcc', 'h5': 12, 'd': 'dblp', 'n': 'DCC'}, {'i': 'conf/visualization', 'h5': 11, 'd': 'dblp', 'n': 'VISUALIZATION'}, {'i': 'journals/cvgip', 'h5': 11, 'd': 'dblp', 'n': 'GM'}, {'i': 'conf/eurographics', 'h5': 7, 'd': 'dblp', 'n': 'EG'}, {'i': 'conf/sma', 'h5': 6, 'd': 'dblp', 'n': 'SPM'}, {'i': 'conf/siggraph', 'h5': 4, 'd': 'dblp', 'n': 'SIGGRAPH'}, {'i': 'conf/pg', 'h5': 0, 'd': 'dblp', 'n': 'PG'}, {'i': 'conf/rt', 'h5': 0, 'd': 'dblp', 'n': 'RT'}, {'i': 'conf/sgp', 'h5': 0, 'd': 'dblp', 'n': 'SGP'}, {'i': 'conf/vissym', 'h5': 0, 'd': 'dblp', 'n': 'VISSYM'}] ,"8": [{'i': 'journals/pami', 'h5': 114, 'd': 'dblp', 'n': 'PAMI'}, {'i': 'conf/cvpr', 'h5': 112, 'd': 'dblp', 'n': 'CVPR'}, {'i': 'conf/par', 'h5': 67, 'd': 'dblp', 'n': 'PAR'}, {'i': 'conf/iccv', 'h5': 58, 'd': 'dblp', 'n': 'ICCV'}, {'i': 'conf/icra', 'h5': 58, 'd': 'dblp', 'n': 'ICRA'}, {'i': 'journals/ijcv', 'h5': 58, 'd': 'dblp', 'n': 'IJCV'}, {'i': 'conf/icml', 'h5': 56, 'd': 'dblp', 'n': 'ICML'}, {'i': 'conf/nips', 'h5': 51, 'd': 'dblp', 'n': 'NIPS'}, {'i': 'journals/jmlr', 'h5': 49, 'd': 'dblp', 'n': 'JMLR'}, {'i': 'conf/acl', 'h5': 48, 'd': 'dblp', 'n': 'ACL'}, {'i': 'journals/ai', 'h5': 48, 'd': 'dblp', 'n': 'AI'}, {'i': 'journals/taslp', 'h5': 46, 'd': 'dblp', 'n': 'TASLP'}, {'i': 'conf/emnlp', 'h5': 45, 'd': 'dblp', 'n': 'EMNLP'}, {'i': 'conf/aaai', 'h5': 44, 'd': 'dblp', 'n': 'AAAI'}, {'i': 'journals/tfs', 'h5': 44, 'd': 'dblp', 'n': 'TFS'}, {'i': 'journals/tec', 'h5': 38, 'd': 'dblp', 'n': 'TEVC'}, {'i': 'conf/ijcai', 'h5': 35, 'd': 'dblp', 'n': 'IJCAI'}, {'i': 'journals/cviu', 'h5': 34, 'd': 'dblp', 'n': 'CVIU'}, {'i': 'journals/ml', 'h5': 33, 'd': 'dblp', 'n': 'ML'}, {'i': 'journals/nn', 'h5': 32, 'd': 'dblp', 'n': 'NN'}, {'i': 'journals/ijar', 'h5': 31, 'd': 'dblp', 'n': 'IJAR'}, {'i': 'journals/tnn', 'h5': 31, 'd': 'dblp', 'n': 'TNNLS'}, {'i': 'journals/neco', 'h5': 30, 'd': 'dblp', 'n': 'NC'}, {'i': 'journals/ec', 'h5': 27, 'd': 'dblp', 'n': 'EC'}, {'i': 'conf/coling', 'h5': 26, 'd': 'dblp', 'n': 'COLING'}, {'i': 'journals/coling', 'h5': 26, 'd': 'dblp', 'n': 'COLING'}, {'i': 'journals/jair', 'h5': 26, 'd': 'dblp', 'n': 'JAIR'}, {'i': 'journals/taffco', 'h5': 26, 'd': 'dblp', 'n': 'TAC'}, {'i': 'conf/kr', 'h5': 24, 'd': 'dblp', 'n': 'KR'}, {'i': 'conf/atal', 'h5': 23, 'd': 'dblp', 'n': 'ATAL'}, {'i': 'journals/aamas', 'h5': 23, 'd': 'dblp', 'n': 'AAMAS'}, {'i': 'conf/aips', 'h5': 20, 'd': 'dblp', 'n': 'ICAPS'}, {'i': 'conf/colt', 'h5': 20, 'd': 'dblp', 'n': 'COLT'}, {'i': 'conf/ecai', 'h5': 20, 'd': 'dblp', 'n': 'ECAI'}, {'i': 'journals/jar', 'h5': 20, 'd': 'dblp', 'n': 'JAR'}, {'i': 'conf/eccv', 'h5': 16, 'd': 'dblp', 'n': 'ECCV'}, {'i': 'journals/tap', 'h5': 16, 'd': 'dblp', 'n': 'TAP'}, {'i': 'conf/ppsn', 'h5': 15, 'd': 'dblp', 'n': 'PPSN'}, {'i': 'conf/uai', 'h5': 15, 'd': 'dblp', 'n': 'UAI'}, {'i': 'conf/iccbr', 'h5': 10, 'd': 'dblp', 'n': 'ICCBR'}, {'i': 'journals/tslp', 'h5': 9, 'd': 'dblp', 'n': 'TSLP'}, {'i': 'journals/tcyb', 'h5': 6, 'd': 'dblp', 'n': 'TCYB'}] ,"9": [{'i': 'conf/chi', 'h5': 71, 'd': 'dblp', 'n': 'CHI'}, {'i': 'conf/cscw', 'h5': 40, 'd': 'dblp', 'n': 'CSCW'}, {'i': 'conf/uist', 'h5': 39, 'd': 'dblp', 'n': 'UIST'}, {'i': 'conf/huc', 'h5': 29, 'd': 'dblp', 'n': 'HUC'}, {'i': 'conf/percom', 'h5': 28, 'd': 'dblp', 'n': 'PERCOM'}, {'i': 'conf/mhci', 'h5': 27, 'd': 'dblp', 'n': 'MHCI'}, {'i': 'journals/ijmms', 'h5': 27, 'd': 'dblp', 'n': 'IJHCS'}, {'i': 'journals/iwc', 'h5': 24, 'd': 'dblp', 'n': 'IWC'}, {'i': 'journals/umuai', 'h5': 23, 'd': 'dblp', 'n': 'UMUAI'}, {'i': 'conf/iui', 'h5': 21, 'd': 'dblp', 'n': 'IUI'}, {'i': 'conf/tabletop', 'h5': 20, 'd': 'dblp', 'n': 'TABLETOP'}, {'i': 'journals/tochi', 'h5': 20, 'd': 'dblp', 'n': 'TOCHI'}, {'i': 'journals/cscw', 'h5': 17, 'd': 'dblp', 'n': 'CSCW'}, {'i': 'journals/ijhci', 'h5': 17, 'd': 'dblp', 'n': 'IJHCI'}, {'i': 'journals/thms', 'h5': 15, 'd': 'dblp', 'n': 'THMS'}, {'i': 'journals/hhci', 'h5': 14, 'd': 'dblp', 'n': 'HCI'}, {'i': 'conf/group', 'h5': 12, 'd': 'dblp', 'n': 'GROUP'}, {'i': 'conf/ecscw', 'h5': 0, 'd': 'dblp', 'n': 'ECSCW'}] ,"10": [{'i': 'journals/bioinformatics', 'h5': 79, 'd': 'dblp', 'n': 'BIOINFORMATICS'}, {'i': 'conf/www', 'h5': 66, 'd': 'dblp', 'n': 'WWW'}, {'i': 'journals/pieee', 'h5': 64, 'd': 'dblp', 'n': 'PIEEE'}, {'i': 'journals/ploscb', 'h5': 61, 'd': 'dblp', 'n': 'PLOSCB'}, {'i': 'journals/tgrs', 'h5': 55, 'd': 'dblp', 'n': 'TGRS'}, {'i': 'journals/tmi', 'h5': 53, 'd': 'dblp', 'n': 'TMI'}, {'i': 'journals/trob', 'h5': 45, 'd': 'dblp', 'n': 'TR'}, {'i': 'journals/tits', 'h5': 41, 'd': 'dblp', 'n': 'TITS'}, {'i': 'journals/jamia', 'h5': 37, 'd': 'dblp', 'n': 'JAMIA'}, {'i': 'journals/bib', 'h5': 35, 'd': 'dblp', 'n': 'BIB'}, {'i': 'conf/cogsci', 'h5': 31, 'd': 'dblp', 'n': 'COGSCI'}, {'i': 'journals/tase', 'h5': 31, 'd': 'dblp', 'n': 'TASE'}, {'i': 'journals/jacm', 'h5': 30, 'd': 'dblp', 'n': 'JACM'}, {'i': 'conf/rtss', 'h5': 24, 'd': 'dblp', 'n': 'RTSS'}, {'i': 'journals/wwwj', 'h5': 23, 'd': 'dblp', 'n': 'WWWJ'}, {'i': 'journals/cj', 'h5': 22, 'd': 'dblp', 'n': 'CJ'}, {'i': 'conf/recomb', 'h5': 18, 'd': 'dblp', 'n': 'RECOMB'}, {'i': 'conf/emsoft', 'h5': 17, 'd': 'dblp', 'n': 'EMSOFT'}, {'i': 'journals/jcst', 'h5': 14, 'd': 'dblp', 'n': 'JCST'}, {'i': 'conf/bibm', 'h5': 13, 'd': 'dblp', 'n': 'BIBM'}, {'i': 'journals/chinaf', 'h5': 13, 'd': 'dblp', 'n': 'CHINAF'}],"11":[{"i": "chemistry", "d": "doaj","n":"DOAJ"}],"12":[{"i": "civil", "d": "doaj","n":"DOAJ"}],"13":[{"i": "education", "d": "doaj","n":"DOAJ"}],"14":[{"i": "electrical", "d": "doaj","n":"DOAJ"}],"15":[{"i": "geology", "d": "doaj","n":"DOAJ"}],"16":[{"i": "mathematics", "d": "doaj","n":"DOAJ"},{"i": "mathematics", "d": "arxiv","n":"ARXIV"}],"17":[{"i": "physics", "d": "doaj","n":"DOAJ"},{"i": "physics", "d": "arxiv","n":"ARXIV"}],"18":[{"i": "psychology", "d": "doaj","n":"DOAJ"}],"19":[{"i": "qfin", "d": "arxiv","n":"ARXIV"}],"20":[{"i": "statistics", "d": "arxiv","n":"ARXIV"}]}
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

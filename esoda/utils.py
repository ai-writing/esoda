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


CORPUS = {"0": [{"i": "bnc", "d": "bnc",'n':"BNC"}], "1":[{'i': 'conf/IEEEpact', 'd': 'dblp', 'n': 'PACT'}, {'i': 'conf/asplos', 'd': 'dblp', 'n': 'ASPLOS'}, {'i': 'conf/cgo', 'd': 'dblp', 'n': 'CGO'}, {'i': 'conf/cloud', 'd': 'dblp', 'n': 'SOCC'}, {'i': 'conf/cnhpca', 'd': 'dblp', 'n': 'HPCA'}, {'i': 'conf/codes', 'd': 'dblp', 'n': 'CODES'}, {'i': 'conf/date', 'd': 'dblp', 'n': 'DATE'}, {'i': 'conf/eurodac', 'd': 'dblp', 'n': 'DAC'}, {'i': 'conf/fast', 'd': 'dblp', 'n': 'FAST'}, {'i': 'conf/fpga', 'd': 'dblp', 'n': 'FPGA'}, {'i': 'conf/hipeac', 'd': 'dblp', 'n': 'HIPC'}, {'i': 'conf/hpdc', 'd': 'dblp', 'n': 'HPDC'}, {'i': 'conf/iccad', 'd': 'dblp', 'n': 'ICCAD'}, {'i': 'conf/iccd', 'd': 'dblp', 'n': 'ICCD'}, {'i': 'conf/icdcs', 'd': 'dblp', 'n': 'ICDCS'}, {'i': 'conf/icpp', 'd': 'dblp', 'n': 'ICPP'}, {'i': 'conf/ics', 'd': 'dblp', 'n': 'ICS'}, {'i': 'conf/ipps', 'd': 'dblp', 'n': 'IPDPS'}, {'i': 'conf/isca', 'd': 'dblp', 'n': 'ISCA'}, {'i': 'conf/itc', 'd': 'dblp', 'n': 'ITC'}, {'i': 'conf/lisa', 'd': 'dblp', 'n': 'LISA'}, {'i': 'conf/mss', 'd': 'dblp', 'n': 'MSST'}, {'i': 'conf/parco', 'd': 'dblp', 'n': 'PARCO'}, {'i': 'conf/performance', 'd': 'dblp', 'n': 'PERFORMANCE'}, {'i': 'conf/podc', 'd': 'dblp', 'n': 'PODC'}, {'i': 'conf/ppopp', 'd': 'dblp', 'n': 'PPOPP'}, {'i': 'conf/rtas', 'd': 'dblp', 'n': 'RTAS'}, {'i': 'conf/sc', 'd': 'dblp', 'n': 'SC'}, {'i': 'conf/sigmetrics', 'd': 'dblp', 'n': 'SIGMETRICS'}, {'i': 'conf/spaa', 'd': 'dblp', 'n': 'SPAA'}, {'i': 'conf/usenix', 'd': 'dblp', 'n': 'USENIX'}, {'i': 'conf/vee', 'd': 'dblp', 'n': 'VEE'}, {'i': 'journals/jpdc', 'd': 'dblp', 'n': 'JPDC'}, {'i': 'journals/jsa', 'd': 'dblp', 'n': 'JSA'}, {'i': 'journals/pe', 'd': 'dblp', 'n': 'PE'}, {'i': 'journals/taas', 'd': 'dblp', 'n': 'TAAS'}, {'i': 'journals/taco', 'd': 'dblp', 'n': 'TACO'}, {'i': 'journals/tc', 'd': 'dblp', 'n': 'TOC'}, {'i': 'journals/tcad', 'd': 'dblp', 'n': 'TCAD'}, {'i': 'journals/tecs', 'd': 'dblp', 'n': 'TECS'}, {'i': 'journals/tocs', 'd': 'dblp', 'n': 'TOCS'}, {'i': 'journals/todaes', 'd': 'dblp', 'n': 'TODAES'}, {'i': 'journals/tos', 'd': 'dblp', 'n': 'TOS'}, {'i': 'journals/tpds', 'd': 'dblp', 'n': 'TPDS'}, {'i': 'journals/trets', 'd': 'dblp', 'n': 'TRETS'}, {'i': 'journals/tvlsi', 'd': 'dblp', 'n': 'TVLSI'}, {'i': 'journals/micro', 'd': 'dblp', 'n': 'MICRO'}, {'i': 'conf/eurosys', 'd': 'dblp', 'n': 'EUROSYS'}],"2":[{'i': 'conf/conext', 'd': 'dblp', 'n': 'CONEXT'}, {'i': 'conf/icnp', 'd': 'dblp', 'n': 'ICNP'}, {'i': 'conf/imc', 'd': 'dblp', 'n': 'IMC'}, {'i': 'conf/infocom', 'd': 'dblp', 'n': 'INFOCOM'}, {'i': 'conf/ipsn', 'd': 'dblp', 'n': 'IPSN'}, {'i': 'conf/iwqos', 'd': 'dblp', 'n': 'IWQOS'}, {'i': 'conf/mobicom', 'd': 'dblp', 'n': 'MOBICOM'}, {'i': 'conf/mobihoc', 'd': 'dblp', 'n': 'MOBIHOC'}, {'i': 'conf/mobisys', 'd': 'dblp', 'n': 'MOBISYS'}, {'i': 'conf/nossdav', 'd': 'dblp', 'n': 'NOSSDAV'}, {'i': 'conf/nsdi', 'd': 'dblp', 'n': 'NSDI'}, {'i': 'conf/secon', 'd': 'dblp', 'n': 'SECON'}, {'i': 'conf/sensys', 'd': 'dblp', 'n': 'SENSYS'}, {'i': 'conf/sigcomm', 'd': 'dblp', 'n': 'SIGCOMM'}, {'i': 'journals/cn', 'd': 'dblp', 'n': 'CN'}, {'i': 'journals/jsac', 'd': 'dblp', 'n': 'JSAC'}, {'i': 'journals/tcom', 'd': 'dblp', 'n': 'TOC'}, {'i': 'journals/tmc', 'd': 'dblp', 'n': 'TMC'}, {'i': 'journals/toit', 'd': 'dblp', 'n': 'TOIT'}, {'i': 'journals/ton', 'd': 'dblp', 'n': 'TON'}, {'i': 'journals/tosn', 'd': 'dblp', 'n': 'TOSN'}, {'i': 'journals/twc', 'd': 'dblp', 'n': 'TWC'}],"3":[{'i': 'conf/acsac', 'd': 'dblp', 'n': 'ACSAC'}, {'i': 'conf/asiacrypt', 'd': 'dblp', 'n': 'ASIACRYPT'}, {'i': 'conf/ccs', 'd': 'dblp', 'n': 'CCS'}, {'i': 'conf/ches', 'd': 'dblp', 'n': 'CHES'}, {'i': 'conf/crypto', 'd': 'dblp', 'n': 'CRYPTO'}, {'i': 'conf/csfw', 'd': 'dblp', 'n': 'CSFW'}, {'i': 'conf/dsn', 'd': 'dblp', 'n': 'DSN'}, {'i': 'conf/esorics', 'd': 'dblp', 'n': 'ESORICS'}, {'i': 'conf/eurocrypt', 'd': 'dblp', 'n': 'EUROCRYPT'}, {'i': 'conf/fse', 'd': 'dblp', 'n': 'FSE'}, {'i': 'conf/ndss', 'd': 'dblp', 'n': 'NDSS'}, {'i': 'conf/pkc', 'd': 'dblp', 'n': 'PKC'}, {'i': 'conf/raid', 'd': 'dblp', 'n': 'RAID'}, {'i': 'conf/sp', 'd': 'dblp', 'n': 'SP'}, {'i': 'conf/srds', 'd': 'dblp', 'n': 'SRDS'}, {'i': 'conf/tcc', 'd': 'dblp', 'n': 'TCC'}, {'i': 'conf/uss', 'd': 'dblp', 'n': 'USS'}, {'i': 'journals/compsec', 'd': 'dblp', 'n': 'COMPSEC'}, {'i': 'journals/dcc', 'd': 'dblp', 'n': 'DCC'}, {'i': 'journals/jcs', 'd': 'dblp', 'n': 'JCS'}, {'i': 'journals/joc', 'd': 'dblp', 'n': 'JOC'}, {'i': 'journals/tdsc', 'd': 'dblp', 'n': 'TDSC'}, {'i': 'journals/tifs', 'd': 'dblp', 'n': 'TIFS'}, {'i': 'journals/tissec', 'd': 'dblp', 'n': 'TISS'}],"4":[{'i': 'conf/caise', 'd': 'dblp', 'n': 'CAISE'}, {'i': 'conf/cp', 'd': 'dblp', 'n': 'CP'}, {'i': 'conf/ecoop', 'd': 'dblp', 'n': 'ECOOP'}, {'i': 'conf/esem', 'd': 'dblp', 'n': 'ESEM'}, {'i': 'conf/etaps', 'd': 'dblp', 'n': 'ETAPS'}, {'i': 'conf/fm', 'd': 'dblp', 'n': 'FM'}, {'i': 'conf/hotos', 'd': 'dblp', 'n': 'HOTOS'}, {'i': 'conf/icfp', 'd': 'dblp', 'n': 'ICFP'}, {'i': 'conf/icse', 'd': 'dblp', 'n': 'ICSE'}, {'i': 'conf/icsm', 'd': 'dblp', 'n': 'ICSM'}, {'i': 'conf/icsoc', 'd': 'dblp', 'n': 'ICSOC'}, {'i': 'conf/icws', 'd': 'dblp', 'n': 'ICWS'}, {'i': 'conf/issre', 'd': 'dblp', 'n': 'ISSRE'}, {'i': 'conf/issta', 'd': 'dblp', 'n': 'ISSTA'}, {'i': 'conf/iwpc', 'd': 'dblp', 'n': 'ICPC'}, {'i': 'conf/kbse', 'd': 'dblp', 'n': 'ASE'}, {'i': 'conf/lctrts', 'd': 'dblp', 'n': 'LCTES'}, {'i': 'conf/middleware', 'd': 'dblp', 'n': 'MIDDLEWARE'}, {'i': 'conf/models', 'd': 'dblp', 'n': 'MODELS'}, {'i': 'conf/oopsla', 'd': 'dblp', 'n': 'OOPSLA'}, {'i': 'conf/osdi', 'd': 'dblp', 'n': 'OSDI'}, {'i': 'conf/pldi', 'd': 'dblp', 'n': 'PLDI'}, {'i': 'conf/popl', 'd': 'dblp', 'n': 'POPL'}, {'i': 'conf/re', 'd': 'dblp', 'n': 'RE'}, {'i': 'conf/sas', 'd': 'dblp', 'n': 'SAS'}, {'i': 'conf/sigsoft', 'd': 'dblp', 'n': 'ESEC'}, {'i': 'conf/sosp', 'd': 'dblp', 'n': 'SOSP'}, {'i': 'conf/vmcai', 'd': 'dblp', 'n': 'VMCAI'}, {'i': 'conf/wcre', 'd': 'dblp', 'n': 'WCRE'}, {'i': 'journals/ase', 'd': 'dblp', 'n': 'ASE'}, {'i': 'journals/ese', 'd': 'dblp', 'n': 'ESE'}, {'i': 'journals/iee', 'd': 'dblp', 'n': 'IETS'}, {'i': 'journals/infsof', 'd': 'dblp', 'n': 'INFSOF'}, {'i': 'journals/jfp', 'd': 'dblp', 'n': 'JFP'}, {'i': 'journals/jss', 'd': 'dblp', 'n': 'JSS'}, {'i': 'journals/re', 'd': 'dblp', 'n': 'RE'}, {'i': 'journals/scp', 'd': 'dblp', 'n': 'SCP'}, {'i': 'journals/smr', 'd': 'dblp', 'n': 'SMR'}, {'i': 'journals/sosym', 'd': 'dblp', 'n': 'SOSYM'}, {'i': 'journals/spe', 'd': 'dblp', 'n': 'SPE'}, {'i': 'journals/stvr', 'd': 'dblp', 'n': 'STVR'}, {'i': 'journals/toplas', 'd': 'dblp', 'n': 'TOPLAS'}, {'i': 'journals/tosem', 'd': 'dblp', 'n': 'TOSEM'}, {'i': 'journals/tsc', 'd': 'dblp', 'n': 'TSC'}, {'i': 'journals/tse', 'd': 'dblp', 'n': 'ITSE'}],"5":[{'i': 'conf/cidr', 'd': 'dblp', 'n': 'CIDR'}, {'i': 'conf/cikm', 'd': 'dblp', 'n': 'CIKM'}, {'i': 'conf/dasfaa', 'd': 'dblp', 'n': 'DASFAA'}, {'i': 'conf/ecml', 'd': 'dblp', 'n': 'ECML'}, {'i': 'conf/edbt', 'd': 'dblp', 'n': 'EDBT'}, {'i': 'conf/icde', 'd': 'dblp', 'n': 'ICDE'}, {'i': 'conf/icdm', 'd': 'dblp', 'n': 'ICDM'}, {'i': 'conf/icdt', 'd': 'dblp', 'n': 'ICDT'}, {'i': 'conf/kdd', 'd': 'dblp', 'n': 'KDD'}, {'i': 'conf/pods', 'd': 'dblp', 'n': 'PODS'}, {'i': 'conf/sdm', 'd': 'dblp', 'n': 'SDM'}, {'i': 'conf/semweb', 'd': 'dblp', 'n': 'ISWC'}, {'i': 'conf/sigir', 'd': 'dblp', 'n': 'SIGIR'}, {'i': 'conf/sigmod', 'd': 'dblp', 'n': 'SIGMOD'}, {'i': 'conf/vldb', 'd': 'dblp', 'n': 'VLDB'}, {'i': 'conf/wsdm', 'd': 'dblp', 'n': 'WSDM'}, {'i': 'journals/aei', 'd': 'dblp', 'n': 'AEI'}, {'i': 'journals/datamine', 'd': 'dblp', 'n': 'DMKD'}, {'i': 'journals/dke', 'd': 'dblp', 'n': 'DKE'}, {'i': 'journals/ejis', 'd': 'dblp', 'n': 'EJIS'}, {'i': 'journals/geoinformatica', 'd': 'dblp', 'n': 'GEOINFORMATICA'}, {'i': 'journals/ipm', 'd': 'dblp', 'n': 'IPM'}, {'i': 'journals/is', 'd': 'dblp', 'n': 'IS'}, {'i': 'journals/isci', 'd': 'dblp', 'n': 'ISCI'}, {'i': 'journals/jasis', 'd': 'dblp', 'n': 'JASIS'}, {'i': 'journals/kais', 'd': 'dblp', 'n': 'KAIS'}, {'i': 'journals/tkdd', 'd': 'dblp', 'n': 'TKDD'}, {'i': 'journals/tkde', 'd': 'dblp', 'n': 'TKDE'}, {'i': 'journals/tods', 'd': 'dblp', 'n': 'TODS'}, {'i': 'journals/tois', 'd': 'dblp', 'n': 'TOIS'}, {'i': 'journals/tweb', 'd': 'dblp', 'n': 'TWEB'}, {'i': 'journals/vldb', 'd': 'dblp', 'n': 'VLDB'}, {'i': 'journals/ws', 'd': 'dblp', 'n': 'WS'}],"6":[{'i': 'conf/cade', 'd': 'dblp', 'n': 'CADE'}, {'i': 'conf/cav', 'd': 'dblp', 'n': 'CAV'}, {'i': 'conf/coco', 'd': 'dblp', 'n': 'CCC'}, {'i': 'conf/compgeom', 'd': 'dblp', 'n': 'SOCG'}, {'i': 'conf/concur', 'd': 'dblp', 'n': 'CONCUR'}, {'i': 'conf/esa', 'd': 'dblp', 'n': 'ESA'}, {'i': 'conf/focs', 'd': 'dblp', 'n': 'FOCS'}, {'i': 'conf/hybrid', 'd': 'dblp', 'n': 'HSCC'}, {'i': 'conf/icalp', 'd': 'dblp', 'n': 'ICALP'}, {'i': 'conf/lics', 'd': 'dblp', 'n': 'LICS'}, {'i': 'conf/soda', 'd': 'dblp', 'n': 'SODA'}, {'i': 'conf/stoc', 'd': 'dblp', 'n': 'STOC'}, {'i': 'journals/algorithmica', 'd': 'dblp', 'n': 'ALGORITHMICA'}, {'i': 'journals/cc', 'd': 'dblp', 'n': 'CC'}, {'i': 'journals/fac', 'd': 'dblp', 'n': 'FAC'}, {'i': 'journals/fmsd', 'd': 'dblp', 'n': 'FMSD'}, {'i': 'journals/iandc', 'd': 'dblp', 'n': 'IANDC'}, {'i': 'journals/informs', 'd': 'dblp', 'n': 'IJOC'}, {'i': 'journals/jcss', 'd': 'dblp', 'n': 'JCSS'}, {'i': 'journals/jgo', 'd': 'dblp', 'n': 'JGO'}, {'i': 'journals/jsc', 'd': 'dblp', 'n': 'JSC'}, {'i': 'journals/mscs', 'd': 'dblp', 'n': 'MSCS'}, {'i': 'journals/siamcomp', 'd': 'dblp', 'n': 'SICOMP'}, {'i': 'journals/talg', 'd': 'dblp', 'n': 'TALG'}, {'i': 'journals/tcs', 'd': 'dblp', 'n': 'TCS'}, {'i': 'journals/tit', 'd': 'dblp', 'n': 'TIT'}, {'i': 'journals/tocl', 'd': 'dblp', 'n': 'TOCL'}, {'i': 'journals/toms', 'd': 'dblp', 'n': 'TOMS'}],"7":[{'i': 'conf/dcc', 'd': 'dblp', 'n': 'DCC'}, {'i': 'conf/eurographics', 'd': 'dblp', 'n': 'EG'}, {'i': 'conf/icassp', 'd': 'dblp', 'n': 'ICASSP'}, {'i': 'conf/icmcs', 'd': 'dblp', 'n': 'ICMCS'}, {'i': 'conf/mir', 'd': 'dblp', 'n': 'ICMR'}, {'i': 'conf/mm', 'd': 'dblp', 'n': 'MM'}, {'i': 'conf/pg', 'd': 'dblp', 'n': 'PG'}, {'i': 'conf/rt', 'd': 'dblp', 'n': 'RT'}, {'i': 'conf/sca', 'd': 'dblp', 'n': 'SCA'}, {'i': 'conf/sgp', 'd': 'dblp', 'n': 'SGP'}, {'i': 'conf/si3d', 'd': 'dblp', 'n': 'SI3D'}, {'i': 'conf/siggraph', 'd': 'dblp', 'n': 'SIGGRAPH'}, {'i': 'conf/sma', 'd': 'dblp', 'n': 'SPM'}, {'i': 'conf/vissym', 'd': 'dblp', 'n': 'VISSYM'}, {'i': 'conf/visualization', 'd': 'dblp', 'n': 'VISUALIZATION'}, {'i': 'journals/cad', 'd': 'dblp', 'n': 'CAD'}, {'i': 'journals/cagd', 'd': 'dblp', 'n': 'CAGD'}, {'i': 'journals/cgf', 'd': 'dblp', 'n': 'CGF'}, {'i': 'journals/cvgip', 'd': 'dblp', 'n': 'GM'}, {'i': 'journals/siamis', 'd': 'dblp', 'n': 'SIAMIS'}, {'i': 'journals/speech', 'd': 'dblp', 'n': 'SPEECH'}, {'i': 'journals/tcsv', 'd': 'dblp', 'n': 'TCSV'}, {'i': 'journals/tip', 'd': 'dblp', 'n': 'TIP'}, {'i': 'journals/tmm', 'd': 'dblp', 'n': 'TMM'}, {'i': 'journals/tog', 'd': 'dblp', 'n': 'TOG'}, {'i': 'journals/tomccap', 'd': 'dblp', 'n': 'TOMCCAP'}, {'i': 'journals/tvcg', 'd': 'dblp', 'n': 'TVCG'}, {'i': 'conf/vr', 'd': 'dblp', 'n': 'VR'}],"8":[{'i': 'conf/aaai', 'd': 'dblp', 'n': 'AAAI'}, {'i': 'conf/acl', 'd': 'dblp', 'n': 'ACL'}, {'i': 'conf/aips', 'd': 'dblp', 'n': 'ICAPS'}, {'i': 'conf/atal', 'd': 'dblp', 'n': 'ATAL'}, {'i': 'conf/coling', 'd': 'dblp', 'n': 'COLING'}, {'i': 'conf/colt', 'd': 'dblp', 'n': 'COLT'}, {'i': 'conf/cvpr', 'd': 'dblp', 'n': 'CVPR'}, {'i': 'conf/ecai', 'd': 'dblp', 'n': 'ECAI'}, {'i': 'conf/eccv', 'd': 'dblp', 'n': 'ECCV'}, {'i': 'conf/emnlp', 'd': 'dblp', 'n': 'EMNLP'}, {'i': 'conf/iccbr', 'd': 'dblp', 'n': 'ICCBR'}, {'i': 'conf/iccv', 'd': 'dblp', 'n': 'ICCV'}, {'i': 'conf/icml', 'd': 'dblp', 'n': 'ICML'}, {'i': 'conf/icra', 'd': 'dblp', 'n': 'ICRA'}, {'i': 'conf/ijcai', 'd': 'dblp', 'n': 'IJCAI'}, {'i': 'conf/kr', 'd': 'dblp', 'n': 'KR'}, {'i': 'conf/nips', 'd': 'dblp', 'n': 'NIPS'}, {'i': 'conf/ppsn', 'd': 'dblp', 'n': 'PPSN'}, {'i': 'conf/uai', 'd': 'dblp', 'n': 'UAI'}, {'i': 'journals/aamas', 'd': 'dblp', 'n': 'AAMAS'}, {'i': 'journals/ai', 'd': 'dblp', 'n': 'AI'}, {'i': 'journals/coling', 'd': 'dblp', 'n': 'COLING'}, {'i': 'journals/cviu', 'd': 'dblp', 'n': 'CVIU'}, {'i': 'journals/ec', 'd': 'dblp', 'n': 'EC'}, {'i': 'journals/ijar', 'd': 'dblp', 'n': 'IJAR'}, {'i': 'journals/ijcv', 'd': 'dblp', 'n': 'IJCV'}, {'i': 'journals/jair', 'd': 'dblp', 'n': 'JAIR'}, {'i': 'journals/jar', 'd': 'dblp', 'n': 'JAR'}, {'i': 'journals/jmlr', 'd': 'dblp', 'n': 'JMLR'}, {'i': 'journals/ml', 'd': 'dblp', 'n': 'ML'}, {'i': 'journals/neco', 'd': 'dblp', 'n': 'NC'}, {'i': 'journals/nn', 'd': 'dblp', 'n': 'NN'}, {'i': 'journals/pami', 'd': 'dblp', 'n': 'PAMI'}, {'i': 'journals/taffco', 'd': 'dblp', 'n': 'TAC'}, {'i': 'journals/tap', 'd': 'dblp', 'n': 'TAP'}, {'i': 'journals/taslp', 'd': 'dblp', 'n': 'TASLP'}, {'i': 'journals/tcyb', 'd': 'dblp', 'n': 'TCYB'}, {'i': 'journals/tec', 'd': 'dblp', 'n': 'TEVC'}, {'i': 'journals/tfs', 'd': 'dblp', 'n': 'TFS'}, {'i': 'journals/tnn', 'd': 'dblp', 'n': 'TNNLS'}, {'i': 'journals/tslp', 'd': 'dblp', 'n': 'TSLP'}, {'i': 'conf/par', 'd': 'dblp', 'n': 'PAR'}],"9":[{'i': 'conf/chi', 'd': 'dblp', 'n': 'CHI'}, {'i': 'conf/cscw', 'd': 'dblp', 'n': 'CSCW'}, {'i': 'conf/ecscw', 'd': 'dblp', 'n': 'ECSCW'}, {'i': 'conf/group', 'd': 'dblp', 'n': 'GROUP'}, {'i': 'conf/huc', 'd': 'dblp', 'n': 'HUC'}, {'i': 'conf/iui', 'd': 'dblp', 'n': 'IUI'}, {'i': 'conf/mhci', 'd': 'dblp', 'n': 'MHCI'}, {'i': 'conf/percom', 'd': 'dblp', 'n': 'PERCOM'}, {'i': 'conf/tabletop', 'd': 'dblp', 'n': 'TABLETOP'}, {'i': 'conf/uist', 'd': 'dblp', 'n': 'UIST'}, {'i': 'journals/cscw', 'd': 'dblp', 'n': 'CSCW'}, {'i': 'journals/hhci', 'd': 'dblp', 'n': 'HCI'}, {'i': 'journals/ijhci', 'd': 'dblp', 'n': 'IJHCI'}, {'i': 'journals/ijmms', 'd': 'dblp', 'n': 'IJHCS'}, {'i': 'journals/iwc', 'd': 'dblp', 'n': 'IWC'}, {'i': 'journals/thms', 'd': 'dblp', 'n': 'THMS'}, {'i': 'journals/tochi', 'd': 'dblp', 'n': 'TOCHI'}, {'i': 'journals/umuai', 'd': 'dblp', 'n': 'UMUAI'}],"10":[{'i': 'conf/bibm', 'd': 'dblp', 'n': 'BIBM'}, {'i': 'conf/cogsci', 'd': 'dblp', 'n': 'COGSCI'}, {'i': 'conf/emsoft', 'd': 'dblp', 'n': 'EMSOFT'}, {'i': 'conf/recomb', 'd': 'dblp', 'n': 'RECOMB'}, {'i': 'conf/rtss', 'd': 'dblp', 'n': 'RTSS'}, {'i': 'conf/www', 'd': 'dblp', 'n': 'WWW'}, {'i': 'journals/bib', 'd': 'dblp', 'n': 'BIB'}, {'i': 'journals/bioinformatics', 'd': 'dblp', 'n': 'BIOINFORMATICS'}, {'i': 'journals/chinaf', 'd': 'dblp', 'n': 'CHINAF'}, {'i': 'journals/cj', 'd': 'dblp', 'n': 'CJ'}, {'i': 'journals/jacm', 'd': 'dblp', 'n': 'JACM'}, {'i': 'journals/jamia', 'd': 'dblp', 'n': 'JAMIA'}, {'i': 'journals/jcst', 'd': 'dblp', 'n': 'JCST'}, {'i': 'journals/pieee', 'd': 'dblp', 'n': 'PIEEE'}, {'i': 'journals/ploscb', 'd': 'dblp', 'n': 'PLOSCB'}, {'i': 'journals/tase', 'd': 'dblp', 'n': 'TASE'}, {'i': 'journals/tgrs', 'd': 'dblp', 'n': 'TGRS'}, {'i': 'journals/tits', 'd': 'dblp', 'n': 'TITS'}, {'i': 'journals/tmi', 'd': 'dblp', 'n': 'TMI'}, {'i': 'journals/trob', 'd': 'dblp', 'n': 'TR'}, {'i': 'journals/wwwj', 'd': 'dblp', 'n': 'WWWJ'}],"11":[{"i": "chemistry", "d": "doaj","n":"DOAJ"}],"12":[{"i": "civil", "d": "doaj","n":"DOAJ"}],"13":[{"i": "education", "d": "doaj","n":"DOAJ"}],"14":[{"i": "electrical", "d": "doaj","n":"DOAJ"}],"15":[{"i": "geology", "d": "doaj","n":"DOAJ"}],"16":[{"i": "mathematics", "d": "doaj","n":"DOAJ"},{"i": "mathematics", "d": "arxiv","n":"ARXIV"}],"17":[{"i": "physics", "d": "doaj","n":"DOAJ"},{"i": "physics", "d": "arxiv","n":"ARXIV"}],"18":[{"i": "psychology", "d": "doaj","n":"DOAJ"}],"19":[{"i": "qfin", "d": "arxiv","n":"ARXIV"}],"20":[{"i": "statistics", "d": "arxiv","n":"ARXIV"}]}
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

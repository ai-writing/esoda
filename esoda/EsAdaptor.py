from elasticsearch import Elasticsearch
from django.conf import settings

defaultCids = ["ecscw", "uist", "chi", "its", "iui", "hci", "ubicomp", "cscw", "acm_trans_comput_hum_interact_tochi_", "user_model_user_adapt_interact_umuai_", "int_j_hum_comput_stud_ijmms_", "mobile_hci"]

class EsAdaptor():
    es = Elasticsearch(settings.ELASTICSEARCH_HOST, timeout=10)
    es.info()
    print 'Connected to Elasticsearch:', es
    index = settings.ELASTICSEARCH_INDEX
    doctype = settings.ELASTICSEARCH_DOCTYPE

    @staticmethod
    def build():
        if not EsAdaptor.es.indices.exists(index=EsAdaptor.index):
            EsAdaptor.es.indices.create(index=EsAdaptor.index)
            mappings = {
                EsAdaptor.doctype: {
                    "properties": {
                        "p": {"type": "integer"},
                        "c": {"type": "text", "index": "not_analyzed"},
                        "t": {
                            "type": "nested",
                            "properties": {
                                "t": {"type": "text", "index": "not_analyzed"},
                                "l": {"type": "text", "fielddata": True, "index": "not_analyzed"}
                            }
                        },
                        "d": {
                            "type": "nested",
                            "properties": {
                                "dt": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "l1": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "l2": {"type": "text", "fielddata": True, "index": "not_analyzed"},
                                "i1": {"type": "text", "index": "not_analyzed"},
                                "i2": {"type": "text", "index": "not_analyzed"}
                            }
                        }
                    }
                }
            }
            EsAdaptor.es.indices.put_mapping(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=mappings)

    @staticmethod
    def search(t, d, ref, cids=defaultCids, sp=0):
        action = {
            "_source": ["p", "c"],
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": [{
                                "terms": {
                                    "c": cids
                                }
                            }]
                        }
                    },
                    "script_score": {
                        "script": {
                            "lang": "painless",
                            "file": "calculate-cost",
                            "params": {
                                "tList": t,
                                "dList": d,
                                "rList": ref
                            }
                        }
                    }
                }
            },
            "script_fields": {
                "sentence": {
                    "script": {
                        "lang": "painless",
                        "file": "highlight-sentence",
                        "params": {
                            "tList": t,
                            "dList": d,
                            "rList": ref
                        }
                    }
                }
            }
        }
        if sp:
            action['size'] = sp

        for tt in t:
            tq = {
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {}
                    }
                }
            }
            tq['nested']['query']['match'] = {'t.l': tt}
            action['query']['function_score']['query']['bool']['must'].append(tq)

        for dd in d:
            dq = {
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": []
                        }
                    }
                }
            }
            if 'dt' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.dt': dd['dt']}})
            if 'i1' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l1': t[dd['i1']]}})
            if 'i2' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l2': t[dd['i2']]}})
            action['query']['function_score']['query']['bool']['must'].append(dq)
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=action, filter_path=[
            'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
        return res['hits']

    @staticmethod
    def collocation(t, cids=defaultCids, sp=0):
        if not t or len(t) > 2:
            return {}
        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": [{
                        "terms": {
                            "c": cids
                        }
                    }]
                }
            },
            "aggs": {
                "d": {
                    "nested": {
                        "path": "d"
                    },
                    "aggs": {
                        "d": {
                            "aggs": {
                                "d": {
                                    "terms": {
                                        "field": "d.dt"
                                    }
                                }
                            },
                            "filter": {
                            }
                        }
                    }
                }
            }
        }

        if len(t) > 1:
            ret = []
            for ps in (('d.l1', 'd.l2'), ('d.l2', 'd.l1')):
                ddq = [{'match': {ps[0]: t[0]}}, {'match': {ps[1]: t[1]}}]
                dq = {
                    "nested": {
                        "path": "d",
                        "query": {
                            "bool": {
                                "must": ddq
                            }
                        }
                    }
                }
                action['query']['bool']['must'].append(dq)
                df = {
                    'bool': {
                        'must': ddq
                    }
                }
                action['aggs']['d']['aggs']['d']['filter'] = df
                ret += EsAdaptor.__checkResult(action)
        else:
            ret = []
            for ps in ('d.l1', 'd.l2'):
                ddq = {'match': {ps: t[0]}}
                dq = {
                    "nested": {
                        "path": "d",
                        "query": ddq
                    }
                }
                action['query'] = dq
                action['aggs']['d']['aggs']['d']['filter'] = ddq
                ret += EsAdaptor.__checkResult(action)

        return ret

    @staticmethod
    def __checkResult(action):
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=action, filter_path=[
            'hits.total', 'aggregations'])
        ret = [False] * 4
        for agg in res['aggregations']['d']['d']['d']['buckets']:
            ret[ord(agg['key']) - 49] = True
            # ord('0') = 48
        return ret

    @staticmethod
    def group(t, d, cids=defaultCids, sp=0):
        if not d or len(d) > 1:
            return {}
        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": [{
                        "terms": {
                            "c": cids
                        }
                    }]
                }
            },
            "aggs": {
                "d": {
                    "nested": {
                        "path": "d"
                    },
                    "aggs": {
                        "d": {
                            "aggs": {
                                "d": {
                                    "terms": {
                                        "size": sp if sp else 10
                                    }
                                }
                            },
                            "filter": {
                                "bool": {
                                    "must": []
                                }
                            }
                        }
                    }
                }
            }
        }

        for i, tt in enumerate(t):
            tq = {
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {}
                    },
                }
            }
            tq['nested']['query']['match'] = {'t.l': tt}
            action['query']['bool']['must'].append(tq)

        dq = [{
            "nested": {
                "path": "d",
                "query": {
                    "bool": {
                        "must": []
                    }
                }
            }
        }]
        dd = d[0]
        ddq = []
        cover = 0
        if 'dt' in dd:
            ddq.append({'match': {'d.dt': str(dd['dt'])}})
            cover |= 1
        if 'l1' in dd and dd['l1'] != '*':
            ddq.append({'match': {'d.l1': dd['l1']}})
            cover |= 2
        if 'l2' in dd and dd['l2'] != '*':
            ddq.append({'match': {'d.l2': dd['l2']}})
            cover |= 4
        dq[0]['nested']['query']['bool']['must'] += ddq

        action['query']['bool']['must'] += dq
        action['aggs']['d']['aggs']['d']['filter']['bool']['must'] += ddq

        st = 'd.dt' if cover == 6 else 'd.l1' if cover == 5 else 'd.l2'
        if cover not in (3, 5, 6):
            return {}

        action['aggs']['d']['aggs']['d']['aggs']['d']['terms']['field'] = st

        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=action, filter_path=[
            'hits.total', 'aggregations'])
        return res

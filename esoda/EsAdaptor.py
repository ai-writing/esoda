from elasticsearch import Elasticsearch
from django.conf import settings


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
    def search(t, d, ref, cids, sp=0):
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
            action['query']['function_score']['query']['bool']['must'].append({
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {'t.l': tt}
                    }
                }
            })

        for dd in d:
            lst = []
            if 'dt' in dd:
                lst.append({'match': {'d.dt': dd['dt']}})
            if 'i1' in dd:
                lst.append({'match': {'d.l1': t[dd['i1']]}})
            if 'i2' in dd:
                lst.append({'match': {'d.l2': t[dd['i2']]}})
            action['query']['function_score']['query']['bool']['must'].append({
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": lst
                        }
                    }
                }
            })
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=action, filter_path=[
            'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
        return res['hits']

    @staticmethod
    def collocation(t, d, cids, sp=0):
        d = [i for i in d if i != '*']
        if not d or len(d) > 2:
            return {}
        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": None
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

        mst = [{
            "terms": {
                "c": cids
            }
        }]

        for tt in t:
            mst.append({
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {'t.l': tt}
                    }
                }
            })

        if len(d) > 1:
            ret = []
            for ps in (('d.l1', 'd.l2'), ('d.l2', 'd.l1')):
                action['query']['bool']['must'] = list(mst)
                ddq = [{'match': {ps[0]: d[0]}}, {'match': {ps[1]: d[1]}}]
                action['query']['bool']['must'].append({
                    "nested": {
                        "path": "d",
                        "query": {
                            "bool": {
                                "must": ddq
                            }
                        }
                    }
                })
                action['aggs']['d']['aggs']['d']['filter'] = {
                    'bool': {
                        'must': ddq
                    }
                }
                ret += EsAdaptor.__checkResult(action)
        else:
            ret = []
            for ps in ('d.l1', 'd.l2'):
                ddq = {'match': {ps: d[0]}}
                action['query'] = {
                    "nested": {
                        "path": "d",
                        "query": ddq
                    }
                }
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
    def group(t, d, cids, sp=0):
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

        for tt in t:
            action['query']['bool']['must'].append({
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {'t.l': tt}
                    },
                }
            })

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

        # import json
        # print json.dumps(action, indent=2)

        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=EsAdaptor.doctype, body=action, filter_path=[
            'hits.total', 'aggregations'])
        return res

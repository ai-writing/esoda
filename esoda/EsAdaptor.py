from elasticsearch import Elasticsearch
from django.conf import settings


class EsAdaptor():
    es = Elasticsearch(settings.ELASTICSEARCH_HOST, timeout=10)
    es.info()
    print 'Connected to Elasticsearch:', es
    index = settings.ELASTICSEARCH_INDEX
    # doctype = settings.ELASTICSEARCH_DOCTYPE

    @staticmethod
    def build():
        if not EsAdaptor.es.indices.exists(index=EsAdaptor.index):
            EsAdaptor.es.indices.create(index=EsAdaptor.index)
            mappings = {
                '_default_': {
                    "properties": {
                        "p": {"type": "integer"},
                        "c": {"type": "keyword"},
                        "t": {
                            "type": "nested",
                            "properties": {
                                "t": {"type": "keyword"},
                                "l": {"type": "keyword"}
                            }
                        },
                        "d": {
                            "type": "nested",
                            "properties": {
                                "dt": {"type": "keyword"},
                                "l1": {"type": "keyword"},
                                "l2": {"type": "keyword"},
                                "i1": {"type": "keyword"},
                                "i2": {"type": "keyword"}
                            }
                        }
                    }
                }
            }
            EsAdaptor.es.indices.put_mapping(index=EsAdaptor.index, body=mappings)

    @staticmethod
    def search(t, d, ref, cids, sp=10):
        mst = []
        for tt in t:
            mst.append({
                "nested": {
                    "path": "t",
                    "query": {
                        "term": {'t.l': tt}
                    }
                }
            })
        for dd in d:
            lst = []
            if 'dt' in dd:
                lst.append({'term': {'d.dt': dd['dt']}})
            if 'i1' in dd:
                lst.append({'term': {'d.l1': t[dd['i1']]}})
            if 'i2' in dd:
                lst.append({'term': {'d.l2': t[dd['i2']]}})
            mst.append({
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": lst
                        }
                    }
                }
            })
        action = {
            "_source": ["p", "c"],
            "size": sp,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": mst
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
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=cids, body=action, filter_path=[
            'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
        return res['hits']

    @staticmethod
    def collocation(t, d, cids, sp=10):
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
                                        "field": "d.dt",
                                        "size": sp
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

        mst = []
        for tt in t:
            mst.append({
                "nested": {
                    "path": "t",
                    "query": {
                        "term": {'t.l': tt}
                    }
                }
            })

        if len(d) > 1:
            ret = []
            for ps in (('d.l1', 'd.l2'), ('d.l2', 'd.l1')):
                action['query']['bool']['must'] = list(mst)
                ddq = [{'term': {ps[0]: d[0]}}, {'term': {ps[1]: d[1]}}]
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
                ret += EsAdaptor.__checkResult(action, cids)
        else:
            ret = []
            for ps in ('d.l1', 'd.l2'):
                ddq = {'term': {ps: d[0]}}
                action['query'] = {
                    "nested": {
                        "path": "d",
                        "query": ddq
                    }
                }
                action['aggs']['d']['aggs']['d']['filter'] = ddq
                ret += EsAdaptor.__checkResult(action, cids)

        return ret

    @staticmethod
    def __checkResult(action, cids):
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=cids, body=action, filter_path=[
            'hits.total', 'aggregations'])
        ret = [False] * 4
        for agg in res['aggregations']['d']['d']['d']['buckets']:
            ret[ord(agg['key']) - 49] = True  # ord('0') = 48
        return ret

    @staticmethod
    def group(t, d, cids, sp=10):
        if not d or len(d) > 1:
            return {}

        dd = d[0]
        ddq = []
        cover = 0
        if 'dt' in dd:
            ddq.append({'term': {'d.dt': str(dd['dt'])}})
            cover |= 1
        if 'l1' in dd and dd['l1'] != '*':
            ddq.append({'term': {'d.l1': dd['l1']}})
            cover |= 2
        if 'l2' in dd and dd['l2'] != '*':
            ddq.append({'term': {'d.l2': dd['l2']}})
            cover |= 4
        if cover not in (3, 5, 6):
            return {}
        st = 'd.dt' if cover == 6 else 'd.l1' if cover == 5 else 'd.l2'

        mst = []
        for tt in t:
            mst.append({
                "nested": {
                    "path": "t",
                    "query": {
                        "term": {'t.l': tt}
                    },
                }
            })
        mst.append({
            "nested": {
                "path": "d",
                "query": {
                    "bool": {
                        "must": ddq
                    }
                }
            }
        })

        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": mst
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
                                        "size": sp,
                                        "field": st
                                    }
                                }
                            },
                            "filter": {
                                "bool": {
                                    "must": ddq
                                }
                            }
                        }
                    }
                }
            }
        }
        # import json
        # print json.dumps(action, indent=2)
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=cids, body=action, filter_path=[
            'hits.total', 'aggregations'])
        return res

    @staticmethod
    def count(t, d, cids):
        mst = []
        for tt in t:
            mst.append({
                "nested": {
                    "path": "t",
                    "query": {
                        "term": {'t.l': tt}
                    },
                }
            })
        for dd in d:
            lst = []
            if 'dt' in dd:
                lst.append({'term': {'d.dt': dd['dt']}})
            if 'l1' in dd:
                lst.append({'term': {'d.l1': dd['l1']}})
            if 'l2' in dd:
                lst.append({'term': {'d.l2': dd['l2']}})
            mst.append({
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": lst
                        }
                    }
                }
            })
        action = {
            "_source": False,
            "query": {
                "bool": {
                    "must": mst
                }
            }
        }
        # import json
        # print json.dumps(action, indent=2)
        res = EsAdaptor.es.search(index=EsAdaptor.index, doc_type=cids, body=action, filter_path=[
            'hits.total'])
        return res

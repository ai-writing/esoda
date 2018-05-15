from elasticsearch import Elasticsearch
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EsAdaptor():
    es = Elasticsearch(settings.ELASTICSEARCH_HOST, timeout=15)
    logger.info('Connected to Elasticsearch: %s', es.info())
    # index = settings.ELASTICSEARCH_INDEX
    # doctype = settings.ELASTICSEARCH_DOCTYPE

    @staticmethod
    def build(db):
        if not EsAdaptor.es.indices.exists(index=db):
            EsAdaptor.es.indices.create(index=db)
        mappings = {
            "mappings": {
                "_default_": {
                    "_all": {"enabled": False},
                    "properties": {
                        "p": {"type": "keyword"},
                        "c": {"type": "keyword"},
                        "a": {
                            "type": "byte",
                            "index": False
                        },
                        "v": {
                            "type": "byte",
                            "index": False
                        },
                        "y": {
                            "type": "short",
                            "index": False
                        },
                        "t": {
                            "type": "nested",
                            "properties": {
                                "t": {
                                    "type": "keyword",
                                    "index": False
                                },
                                "l": {"type": "keyword"}
                            }
                        },
                        "d": {
                            "type": "nested",
                            "properties": {
                                "dt": {
                                    "type": "keyword",
                                    "eager_global_ordinals": True
                                },
                                "l1": {
                                    "type": "keyword",
                                    "eager_global_ordinals": True
                                },
                                "l2": {
                                    "type": "keyword",
                                    "eager_global_ordinals": True
                                },
                                "i1": {
                                    "type": "keyword",
                                    "index": False
                                },
                                "i2": {
                                    "type": "keyword",
                                    "index": False
                                }
                            }
                        }
                    }
                }
            }
        }
        EsAdaptor.es.indices.put_mapping(index=db, body=mappings)

    @staticmethod
    def cidsearch(index, body, filter_path):
        #if doc_type in ('_all', ['_all']):
        return EsAdaptor.es.search(index=index, body=body, filter_path=filter_path)
        # else:
        #     return EsAdaptor.es.search(index=index, doc_type=doc_type, body=body, filter_path=filter_path)

    @staticmethod
    def get_action(t, d, cids):
        mst = EsAdaptor.check_type(cids)
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
            "size": 0,
            "query": {
                "bool": {
                    "must": mst
                }
            }
        }
        return action
        

    @staticmethod
    def msearch(action):
        if action:
            resp = EsAdaptor.es.msearch(body = action)
            return resp['responses']
        else:
            return []

    @staticmethod
    def check_type(cids):
        if cids in ('_all', ['_all']):
            return []
        else:
            return [{ "terms": { "c": cids  }}]

    @staticmethod
    def search(t, d, ref, dbs, cids, sp=10):
        mst = EsAdaptor.check_type(cids)
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
            "terminate_after": 10000,
            "query": {
                "function_score": {
                    "query": {
                        "bool": {
                            "must": mst
                        }
                    },
                    "script_score": {
                        "script": {
                            "id": "calculate-cost",
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
                        "id": "highlight-sentence",
                        "params": {
                            "tList": t,
                            "dList": d,
                            "rList": ref
                        }
                    }
                }
            }
        }
        res = EsAdaptor.cidsearch(index=dbs, body=action, filter_path=[
            'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
        return res['hits']

    @staticmethod
    def collocation(t, d, dbs, cids, sp=10):
        d = [i for i in d if i != '*']
        if not d or len(d) > 2:
            return {}
        action = {
            "size": 0,
            "query": {
                "bool": {
                    "must": []
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

        mst = EsAdaptor.check_type(cids)
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
            #for ps in (('d.l1', 'd.l2'), ('d.l2', 'd.l1')):
            action['query']['bool']['must'] += mst
            ddq = [{'term': {'d.l1': d[0]}}, {'term': {'d.l2': d[1]}}]
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
            ret += EsAdaptor.__checkResult(action, dbs, cids)
        else:
            ret = []
            action['query']['bool']['must'] += mst
            for ps in ('d.l1', 'd.l2'):
                ddq = {'term': {ps: d[0]}}
                action['query']['bool']['must'].append({
                    "nested": {
                        "path": "d",
                        "query": ddq
                    }
                })
                action['aggs']['d']['aggs']['d']['filter'] = ddq
                ret += EsAdaptor.__checkResult(action, dbs, cids)

        return ret

    @staticmethod
    def __checkResult(action, dbs, cids):
        res = EsAdaptor.cidsearch(index=dbs, body=action, filter_path=[
            'hits.total', 'aggregations'])
        ret = [False] * 4
        for agg in res['aggregations']['d']['d']['d']['buckets']:
            ret[ord(agg['key']) - 49] = True  # ord('0') = 48
        return ret

    @staticmethod
    def group(t, d, dbs, cids, sp=39):
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

        mst = EsAdaptor.check_type(cids)
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
            "size": 0,
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
                                        "shard_size": int(sp * 2 + 10),
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
        res = EsAdaptor.cidsearch(index=dbs, body=action, filter_path=[
            'hits.total', 'aggregations'])
        return res

    @staticmethod
    def count(t, d, dbs, cids):
        mst = EsAdaptor.check_type(cids)
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
        res = EsAdaptor.cidsearch(index=dbs, body=action, filter_path=[
            'hits.total'])
        return res

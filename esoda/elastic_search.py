#!/usr/bin/env python
# encoding: utf-8


def elastic_search(es, t, d, sp=0):
    action = {
        "_source": ["p", "c"],
        "query": {
            "bool": {
                "must": []
            }
        }
    }
    if sp:
        action['size'] = sp
    if t:
        for i, tt in enumerate(t):
            tq = {
                "nested": {
                    "path": "t",
                    "query": {
                        "match": {}
                    },
                    "inner_hits": {
                        "_source": False
                    }
                }
            }
            tq['nested']['query']['match'] = {'t.l': tt}
            tq['nested']['inner_hits']['name'] = 'd%d' % i
            action['query']['bool']['must'].append(tq)

    if d:
        for i, dd in enumerate(d):
            dq = {
                "nested": {
                    "path": "d",
                    "query": {
                        "bool": {
                            "must": []
                        }
                    },
                    "inner_hits": {
                        "_source": {
                            "includes": ["d.i1", "d.i2"]
                        }
                    }
                }
            }
            if 'dt' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.dt': str(dd['dt'])}})
            if 'l1' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l1': dd['l1']}})
            if 'l2' in dd:
                dq['nested']['query']['bool']['must'].append({'match': {'d.l2': dd['l2']}})
            dq['nested']['inner_hits']['name'] = 'd%d' % i
            action['query']['bool']['must'].append(dq)
    res = es.search(index='test', doc_type='sentences', body=action, filter_path=[
        'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.inner_hits.d*.hits.hits._source', 'hits.hits.inner_hits.t*.hits.hits._nested.offset'])
    return res['hits']


def elastic_search2(es, t, d, ref, sp=0):
    action = {
        "_source": ["p", "c"],
        "query": {
            "function_score": {
                "query": {
                    "bool": {
                        "must": []
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
    if t:
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

    if d:
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
    res = es.search(index='test', doc_type='sentences', body=action, filter_path=[
        'hits.total', 'hits.hits._id', 'hits.hits._source', 'hits.hits.fields'])
    # res = es.search(index='test', doc_type='sentences', body=action)
    return res['hits']


def elastic_group(es, t, d, sp=0):
    if not d or len(d) > 1:
        return {}
    action = {
        "_source": False,
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

    if t:
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

    if d:
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
        if 'dt' in dd:
            ddq.append({'match': {'d.dt': str(dd['dt'])}})
        if 'l1' in dd:
            ddq.append({'match': {'d.l1': dd['l1']}})
        if 'l2' in dd:
            ddq.append({'match': {'d.l2': dd['l2']}})
        dq[0]['nested']['query']['bool']['must'] += ddq

        action['query']['bool']['must'] += dq
        action['aggs']['d']['aggs']['d']['filter']['bool']['must'] += ddq

        cnt = 0
        st = ''
        if 'dt' not in dd:
            st = 'd.dt'
            cnt += 1
        if 'l1' not in dd:
            st = 'd.l1'
            cnt += 1
        if 'l2' not in dd:
            st = 'd.l2'
            cnt += 1

        if cnt != 1:
            return {}

        action['aggs']['d']['aggs']['d']['aggs']['d']['terms']['field'] = st

    res = es.search(index='test', doc_type='sentences', body=action, filter_path = [
        'hits.total', 'aggregations'])
    return res

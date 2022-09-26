import os
from datetime import datetime, timedelta
from paddle4cjml.cjml_clas import CjmlClas
from elasticsearch import Elasticsearch

from cjml_utils.img_util import download_img

cls = {
    1000: 0,
    1090: 0,
    1180: 0,
    1270: 0,
    1315: 0,
    2000: 0,
    3000: 0,
    4000: 0,
    4045: 0,
    4090: 0,
    4135: 0,
    4180: 0,
    4225: 0,
    4270: 0,
    4315: 0,
}


def es_go(es_url, es_auth, index, st, et):
    es = Elasticsearch(hosts=es_url, http_auth=es_auth)
    st = st.isoformat(sep='T', timespec='microseconds') + '+08:00'
    et = et.isoformat(sep='T', timespec='microseconds') + '+08:00'
    print(st)
    print(et)
    query = {
            "track_total_hits": True,
             "query": {
                 "bool": {
                     "must": [{
                         "term": {
                             "IsSacn": 1
                         }
                     }
                     ],
                     "filter": {
                         "range": {
                             "CreateTime": {
                                 "gt": st,
                                 "lt": et
                             }
                         }
                     }
                 }
             },
             "sort": [
                 {
                     "CreateTime": {
                         "order": "desc",
                         "unmapped_type": "date"
                     }
                 }
             ]
             }

    # res_count = es.count(index=index, body=count_body, request_timeout=10000)
    # total_size = res_count['count']

    # results = es.search(index=index, body=query, size=100, request_timeout=1000)['hits']['hits']

    page = es.search(index=index, body=query, scroll='5m', size=10000, request_timeout=1000)
    # 第一页结果,为list类型
    results = page['hits']['hits']

    sid = page['_scroll_id']
    scroll_size = page['hits']['total']['value']

    while scroll_size > 0:
        print(len(results))
        page = es.scroll(scroll_id=sid, scroll='2m')
        sid = page['_scroll_id']
        results += page['hits']['hits']
        scroll_size = len(page['hits']['hits'])

    return [x["_source"]["OrignalImage"] for x in results]


def start_clas(path_list, save_clas_dir, max_size):
    clas = CjmlClas()
    for path in path_list:
        try:
            clas_res = clas.get_image_class(path)
        except Exception as e:
            print("error img")
            continue
        if cls[clas_res] < max_size:
            save_dir = save_clas_dir + str(clas_res) + "/"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            download_img(save_dir, path)
            cls[clas_res] += 1
            print("----------->", clas_res, " ", cls[clas_res])
        else:
            sum_r = 0
            for v in cls.values():
                sum_r += v
                if sum_r > 69980:
                    return


def start_fetch_from_es():
    url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200"
    auth = ('wujs', 'Wujs!2022')
    idx = "vinscanresult_behaviorlog_*"
    today = datetime.today()
    start_time = datetime(today.year, 7, 5)
    end_time = start_time + timedelta(days=1)
    return es_go(url, auth, idx, start_time, end_time)


if __name__ == '__main__':
    urls = start_fetch_from_es()
    res_dir = "clas/"
    size = 5000
    start_clas(urls, res_dir, size)

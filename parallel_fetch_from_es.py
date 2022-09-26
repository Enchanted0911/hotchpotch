import multiprocessing.dummy as parallel
import os
import shutil
from datetime import datetime, timedelta
from functools import partial

from elasticsearch import Elasticsearch

from cjml_utils.file_util import write_str_list_to_txt
from cjml_utils.img_util import download_img
from paddle4cjml.cjml_clas import CjmlClas

cls = {
    1000: 0,
    1090: 0,
    1180: 0,
    1270: 0,
    1315: 0,
    2000: 10000,
    3000: 10000,
    4000: 10000,
    4045: 0,
    4090: 10000,
    4135: 0,
    4180: 10000,
    4225: 0,
    4270: 10000,
    4315: 0,
}
save_clas_dir = "parallel_clas/"
max_size = 10000


def es_go(es_url, es_auth, index, st, et, cnt=-1):
    # 2022-06-07T00:00:00.000000+08:00
    es = Elasticsearch(hosts=es_url, http_auth=es_auth)
    st = st.isoformat(sep='T', timespec='microseconds') + '+08:00'
    et = et.isoformat(sep='T', timespec='microseconds') + '+08:00'
    print(st)
    print(et)
    print("esgo cnt:", cnt)
    if cnt == -1 or cnt > 10000:
        query = {
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "IsSacn": 0
                            }
                        },
                        {
                            "exists": {
                                "field": "OrignalImage"
                            }
                        },
                        {
                            "term": {
                                "ClientType": 5
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
            "size": cnt,
            "sort": [
                {
                    "CreateTime": {
                        "order": "desc",
                        "unmapped_type": "date"
                    }
                }
            ]
        }
        page = es.search(index=index, body=query, scroll='5m', size=10000, request_timeout=1000)
        # 第一页结果,为list类型
        results = page['hits']['hits']

        sid = page['_scroll_id']
        scroll_size = page['hits']['total']['value']

        while scroll_size > 0 and (len(results) < cnt or cnt == -1):
            print(len(results))
            page = es.scroll(scroll_id=sid, scroll='2m')
            sid = page['_scroll_id']
            results += page['hits']['hits']
            scroll_size = len(page['hits']['hits'])
    else:
        query = {
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "IsSacn": 0
                            }
                        },
                        {
                            "exists": {
                                "field": "OrignalImage"
                            }
                        },
                        {
                            "term": {
                                "ClientType": 5
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
            "sort": {
                "_script": {
                    "script": "Math.random()",
                    "type": "number",
                    "order": "asc"
                }
            }
        }
        results = es.search(index=index, body=query, size=cnt, request_timeout=1000)['hits']['hits']

    return [(x["_source"]["CroppedImage"], x["_source"]["ResultVinCode"]) for x in results]


def es_go_vin_image_url(es_url, es_auth, index, st, et):
    es = Elasticsearch(hosts=es_url, http_auth=es_auth)
    st = st.isoformat(sep='T', timespec='microseconds') + '+08:00'
    et = et.isoformat(sep='T', timespec='microseconds') + '+08:00'
    print(st)
    print(et)
    query = {
        "track_total_hits": True,
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "IsSacn": 0
                        }
                    },
                    {
                        "exists": {
                            "field": "OrignalImage"
                        }
                    }
                ],
                "must_not": [{
                    "term": {
                        "OrignalImage": 1
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

    return [str(x["_source"]["OrignalImage"]) + " " + str(x["_source"]["ResultVinCode"]) for x in results]


def parallel_process(process, path_list):
    pool = parallel.Pool(12)
    pool.map(process, path_list)
    pool.close()
    pool.join()


def process_clas(path):
    try:
        raw_path = download_img(save_clas_dir, path)
        clas = CjmlClas()
        clas_res = clas.get_image_class(raw_path)
    except Exception as e:
        print("error img")
        return
    if cls[clas_res] < max_size:
        save_dir = save_clas_dir + str(clas_res) + "/"
        des_path = save_dir + raw_path[raw_path.rfind('/') + 1:]
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        # download_img(save_dir, path)
        shutil.move(raw_path, des_path)
        cls[clas_res] += 1
        print("----------->", clas_res, " ", cls[clas_res])
    else:
        try:
            os.remove(raw_path)
        except Exception as e:
            print("remove error")
        sum_r = 0
        for v in cls.values():
            sum_r += v
            if sum_r > 69980:
                print("clas done!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")


def start_fetch_from_es(month, day, cnt=-1):
    url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200"
    auth = ('wujs', 'Wujs!2022')
    idx = "vinscanresult_behaviorlog_*"
    today = datetime.today()
    start_time = datetime(today.year, month, day)
    end_time = start_time + timedelta(days=1)
    print("start_fetch_from_es cnt:", cnt)
    return es_go(url, auth, idx, start_time, end_time, cnt)


def download_img_vin_url_map_from_es(cnt=-1):
    url_vin = start_fetch_from_es(9, 15, cnt)
    url_vin_map4txt = [str(x[0]) + " " + str(x[1]) for x in url_vin]
    urls = [x[0] for x in url_vin]
    des_dir = "D:/vin_scan_imgs/"
    pfunc = partial(download_img, des_dir)
    write_str_list_to_txt(url_vin_map4txt, "20220915_vin_url.txt")
    parallel_process(pfunc, urls)


def save_vin_image_url():
    url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200"
    auth = ('wujs', 'Wujs!2022')
    idx = "vinscanresult_behaviorlog_*"
    today = datetime.today()
    start_time = datetime(today.year, 7, 21)
    end_time = start_time + timedelta(days=1)
    vin_url = es_go_vin_image_url(url, auth, idx, start_time, end_time)
    write_str_list_to_txt(vin_url, "20220721_vin_url.txt")


if __name__ == '__main__':
    download_img_vin_url_map_from_es()

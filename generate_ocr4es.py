from paddle4cjml.cjml_ocr import *
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from evaluation import *

det_model_dir = 'ocr_infer/det'
rec_model_dir = 'ocr_infer/rec'
cls_model_dir = 'ocr_infer/cls'

rec_char_dict_path = 'dict/ppocr_keys_v1.txt'


def cjml_ocr_pdf(image_dir):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
    ocr = CjmlOcr(model_args)
    res = ocr.ocr(image_dir, use_decode=False, use_location=True)
    return res


def check_contain_ch_and_eng(check_str):
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff' or 'a' <= ch <= 'z' or 'A' <= ch <= 'Z':
            return True
    return False


def insert2es(image_dir):
    res = cjml_ocr_pdf(image_dir)
    url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200"
    auth = ('wujs', 'Wujs!2022')
    idx = "book_ocr_detail"
    es = Elasticsearch(hosts=url, http_auth=auth)
    fail_list = []
    for k, v in res.items():
        page_inner = ''
        page_outer = k[k.rfind('_') + 1: k.rfind('.')]
        try:
            page_inner = gain_page(v)
        except Exception as e:
            print('error', k, e)
            fail_list.append(k)
        print("this is page ----------", page_inner)
        action = [{
            "_index": idx,
            "_source": {
                "title": k[:k.rfind('_')],
                "confidence": x[1][1],
                "text": x[1][0],
                "location.left_up": x[0][0],
                "location.right_up": x[0][1],
                "location.right_down": x[0][2],
                "location.left_down": x[0][3],
                "page_inner": page_inner,
                "page_outer": int(page_outer)
            }
        } for x in v]
        helpers.bulk(es, action)
    return fail_list


def gain_page(page_content):
    min_y = page_content[0][0][0][1]
    prepare_list = []
    prepare_list2 = []
    for x in page_content:
        if abs(x[0][0][1] - min_y) < 10 and not check_contain_ch_and_eng(x[1][0]):
            prepare_list.append(x[1][0])
        elif abs(x[0][0][1] - min_y) > 10:
            break
    if len(prepare_list) == 1:
        return prepare_list[0]
    else:
        for page in prepare_list:
            if len(re.sub('[0-9]', '', page)) == 1:
                prepare_list2.append(page)
        if len(prepare_list2) == 1:
            return prepare_list2[0]
        else:
            for page in prepare_list2:
                if re.sub('[0-9]', '', page) == '-':
                    return page
    raise Exception('gain page num error!!!')


def supply_page_inner(page_outer, page_inner):
    url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200防止误点"
    auth = ('wujs', 'Wujs!2022')
    idx = "book_ocr_detail"
    es = Elasticsearch(hosts=url, http_auth=auth)
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "page_outer": page_outer
                        }
                    },
                    {
                        "term": {
                            "title.keyword": "吉利缤瑞电路图"
                        }
                    }
                ]
            }
        },
        "script": {
            "inline": "ctx._source.page_inner = params.page_inner",
            "params": {
                "page_inner": page_inner
            },
            "lang": "painless"
        }
    }
    es.update_by_query(index=idx, body=body)


if __name__ == '__main__':
    # cjml_dir = "temp_cjml_demo"
    # cjml_ocr_pdf(cjml_dir)
    fail = insert2es("ocr4nlp_img/吉利缤瑞电路图")
    fail = insert2es("temp_cjml_demo")




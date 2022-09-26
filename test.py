import base64
import json
import re
import shutil
import threading
import time
from datetime import datetime, timedelta
from multiprocessing import shared_memory
from urllib.parse import urlencode, quote_plus, quote

import cv2
import numpy as np
import requests
import urllib3
import multiprocessing.dummy as parallel

from cjml_utils.file_util import get_image_file_list


def es_go(start_time, end_time):
    st = start_time.isoformat(sep='T', timespec='microseconds') + '+08:00'
    et = end_time.isoformat(sep='T', timespec='microseconds') + '+08:00'
    search_url = "http://es-cn-tl32ljolq000ewdl0.public.elasticsearch.aliyuncs.com:9200/vinscanresult_behaviorlog_202206/_search"
    query = {"track_total_hits": True,
             "query": {
                 "bool": {
                     "must": [{
                         "term": {
                             "IsSacn": 0
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
             "from": 10,
             "size": 15,
             "sort": [
                 {
                     "CreateTime": {
                         "order": "desc",
                         "unmapped_type": "date"
                     }
                 }
             ]
             }
    query = json.dumps(query)
    headers = {'Accept': 'application/json', 'Content-type': 'application/json'}
    r = requests.get(search_url, data=query, auth=('wujs', 'Wujs!2022'), verify=False, headers=headers)
    result = json.loads(r.text)
    total = result["hits"]["total"]["value"]
    items = result["hits"]["hits"]
    for item in items:
        source = item["_source"]

        vin = source["ResultVinCode"]

        imageUrl = source["OrignalImage"]

        createdAt = source["CreateTime"]
        print(vin, imageUrl, createdAt)

    print(total)
    print(len(items))


def do_something(txt, seconds):
    with open("123w.txt", 'w') as f:
        f.write(txt)
        print("t1 write 1")
        time.sleep(seconds)
        f.write(txt)
        print("t1 write 2")
        print(txt)


def do_something1(txt, seconds):
    with open("123w.txt", 'w') as f:
        time.sleep(1)
        f.write(txt)
        print("t2 write 1")
        time.sleep(seconds)
        f.write(txt)
        print("t2 write 2")
        print(txt)


def io_go():
    t1 = threading.Thread(target=do_something, args=("123", 2))
    t2 = threading.Thread(target=do_something1, args=("wjs", 2))
    t1.start()
    t2.start()


def a_te():
    today = datetime.today()
    st = datetime(today.year, 7, 9)
    et = st + timedelta(days=1)
    st = st.isoformat(sep='T', timespec='microseconds') + '+08:00'
    et = et.isoformat(sep='T', timespec='microseconds') + '+08:00'
    print(st)
    print(et)


def horizontal_vertical_depart(src_dir, des_dir):
    image_path_list = get_image_file_list(src_dir)
    for i in image_path_list:
        im = cv2.imread(i)
        h, w, _ = im.shape
        if h > w:
            shutil.move(i, des_dir)


def iurl():
    uuu = "http://192.168.100.117:9999/20210415/"
    httpx = urllib3.PoolManager()
    res = httpx.urlopen("GET", uuu)
    # res = requests.get(uuu)

    print(res.data.decode())
    subUrls = re.findall(r'<a.*?href=".*?">(.*?)</a>', res.data.decode())
    print(subUrls)


def shm():
    with open(r"D:\workspace\paddleocr\temp_err\08041.jpg",
              'rb') as file:
        image = file.read()
    data = np.frombuffer(image, np.uint8)
    im = cv2.imdecode(data, cv2.IMREAD_COLOR)

    im_shape = im.shape
    shm = shared_memory.SharedMemory(create=True, size=99999999)
    shm.buf[: im.nbytes] = im.tobytes()
    shm_name = shm.name
    print(shm_name)
    while True:
        pass


def gain_yitu():
    # vin_ocr_url = "http://172.16.30.125:9998/ocr/prediction"
    # vin_ocr_url = "http://192.168.70.21:9998/ocr/prediction"
    # vin_ocr_url = "http://172.16.30.140:8080/OcrWeb/servlet/PageOcrServlet"
    # vin_ocr_url = "http://172.16.30.140:8080/OcrWeb/servlet/OcrServlet"
    # vin_ocr_url = "http://172.16.30.140:8080/OcrWeb/servlet/OcrServlet"
    vin_ocr_url = "http://172.16.20.205/OcrWeb/servlet/OcrServlet"

    with open(r"D:\workspace\paddleocr\temp_err\0926a.jpg",
              'rb') as file:
        image = file.read()
    image = base64.b64encode(image).decode()
    data = {"filedata": image, "pid": "1"}
    data = urlencode(data)
    head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
    st = time.time()
    r = requests.post(url=vin_ocr_url, timeout=(5, 30), headers=head, data=data)
    et = time.time()
    print("cost time ---", et - st)
    print(r)
    print(r.text)
    if r.json()['ErrorCode'] == '0':
        print(r.json()['VIN'])


def parallel_process(process, path_list):
    pool = parallel.Pool(12)
    pool.map(process, path_list)
    pool.close()
    pool.join()


if __name__ == '__main__':
    gain_yitu()
    # s = "中DKDSFJ13432EWFGWGFWG465"
    # vin = re.search("(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{16,20}", s)
    # print(vin)
    # print(vin.group())


import base64
import json
import os
import time

import cv2
import numpy as np
import requests


def gain_data_list(image, cls):
    return [
        {"key": ["image", "mode", "fetch_back"], "value": [image, "000", "0"]},
        {"key": ["image", "mode", "fetch_back"], "value": [image, "100", "0"]},
        {"key": ["image", "mode", "fetch_back"], "value": [image, "XXX", "0"]},
        {"key": ["image", "mode", "fetch_back"], "value": [image, "XXX", "1"]},
        {"key": ["image", "expect_cls"], "value": [image, cls[0]]},
        {"key": ["image", "expect_cls"], "value": [image, cls[0] + '2']},
        {"key": ["image", "cls", "expect_cls"], "value": [image, "-1", "N"]},
        {"key": ["image", "cls", "expect_cls"], "value": [image, "-1", "Y"]},
        {"key": ["image", "cls"], "value": [image, "-1"]},
        {"key": ["image", "cls"], "value": [image, cls]},
        {"key": ["image"], "value": [image]},
        {"key": ["image", "expect_cls"], "value": [image, "V"]},
        {"key": ["image", "expect_cls"], "value": [image, "V" + cls[0]]}
    ]


def warm_up_prod_all(vin_ocr_url):
    warm_up_pic_dir = r"D:\wjs\PycharmProjects\static\pic\ocr_test_set"
    warm_up_pics = os.listdir(warm_up_pic_dir)
    succ = 0
    for pic in warm_up_pics:
        pic_path = warm_up_pic_dir + "/" + pic
        with open(pic_path, 'rb') as file:
            image = file.read()
        image = base64.b64encode(image).decode()
        cls = pic[:4]
        for d in gain_data_list(image, cls):
            data = d
            st = time.time()
            r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 30))
            et = time.time()
            print("cost time ---", et - st)

            print(r.json().keys())
            # print(r.json()["err_no"], r.json()["value"][0], r.json()["value"][1], r.json()["value"][2], r.json()["value"][3] == "")
            print(r.json()["err_no"], r.json()["value"][0], r.json()["value"][1], r.json()["value"][2])
            succ += int(r.json()["err_no"])

    if succ == 0:
        print("succ---------!!!!!")
    else:
        print("err-------!!!!!!!")


def warm_up4test(vin_ocr_url):

    # with open(r"../test.jpg",
    #           'rb') as file:
    with open(r"D:\workspace\paddleocr\temp_err\0919.jpg",
              'rb') as file:
        # with open(r"D:\ocr_test_set\5000.jpg",
        #             'rb') as file:
    # with open(r"D:\vin_eval_5k\vin_android_1661748061645_47644c1006ce4ba6942fd609c9f1761f.jpg",
    #               'rb') as file:
        image = file.read()
    image = base64.b64encode(image).decode()
    # data = {"key": ["image", "cls", "expect_cls", "mode", "fetch_back"], "value": [image, "-1", "Y", "XXX", "0"]}
    # data = {"key": ["image", "cls", "fetch_back"], "value": [image, "4000", "1"]}
    # data = {"key": ["image", "cls", "expect_cls"], "value": [image, "-1", "N"]}
    data = {"key": ["image", "expect_cls"], "value": [image, "Y"]}
    # data = {"key": ["image", "cls"], "value": [image, "5000"]}
    # data = {"key": ["image"], "value": [image]}
    # print(json.dumps(data))
    st = time.time()

    headers = {'Content-Type': 'application/json'}
    r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 300), headers=headers)
    et = time.time()
    print("cost time ---", et - st)
    print(r.json())
    print(r.json().keys())
    print(r.json()["err_no"])
    print(r.json()["value"][0])
    print(r.json()["value"][1])
    print(r.json()["value"][2])
    if 'raw' in r.json()["key"]:
        print(r.json()["value"][5])
    # print(r.json()["value"][4])
    # print(r.json()["key"])
    # b64_im = r.json()["value"][3]
    # if b64_im != "":
    #     data = base64.b64decode(b64_im)
    #     data = np.frombuffer(data, np.uint8)
    #     im = cv2.imdecode(data, cv2.IMREAD_COLOR)
    #     cv2.imwrite("b64_im.jpg", im)


def ocr_predict(image_path):
    alpha_ocr_service_url = "http://192.168.70.21:9798/ocr/prediction"

    with open(image_path, 'rb') as file:
        image = base64.b64encode(file.read()).decode('utf8')

    data = {"key": ["image"], "value": [image]}

    r = requests.post(url=alpha_ocr_service_url, data=json.dumps(data), timeout=(5, 15))
    jresult = r.json()
    bytes_img = jresult['value'][2]

    data = base64.b64decode(bytes_img.encode('utf8'))

    ocr_service_url = 'http://192.168.70.20:9899/predict'
    file = {"img": ("file_name.jpg", data, "image/jpg")}
    r = requests.post(url=ocr_service_url, files=file, timeout=(5, 15))
    print(r.json())
    print(type(bytes_img))


if __name__ == '__main__':
    # vin_ocr_url = "http://172.16.30.125:9998/ocr/prediction"
    # vin_ocr_url = "http://192.168.70.21:9998/ocr/prediction"
    # vin_ocr_url = "http://192.168.60.30:9998/ocr/prediction"
    # vin_ocr_url = "http://120.26.64.17:9998/ocr/prediction"
    vin_ocr_url = "http://172.16.30.151:80/ocr/prediction"
    # vin_ocr_url = "http://192.168.70.36:9998/ocr/prediction"

    # pic_url = "https://cjml.oss-cn-shanghai.aliyuncs.com/test/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20220919150045.jpg"
    # data = {"key": ["url", "expect_cls"], "value": [pic_url, "V"]}
    # st = time.time()
    # headers = {'Content-Type': 'application/json'}
    # r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 300), headers=headers)
    # et = time.time()
    # print("cost time ---", et - st)
    # print(r.json())
    warm_up_prod_all(vin_ocr_url)
    # warm_up4test(vin_ocr_url)

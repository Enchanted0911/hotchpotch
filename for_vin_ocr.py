import base64
import json
import os
import shutil
import time
from functools import partial
from urllib.parse import urlencode

import requests

from cjml_utils.file_util import get_image_file_list, write_str_list_to_txt
from cjml_utils.parallel_util import parallel_process
from cjml_utils.visual_error import visual_diff_vin


def compare_vin(img_dir, compare_txt, res_txt_path):
    res_list = []
    image_vin = {}
    vin_ocr_url = "http://192.168.70.21:9998/ocr/prediction"

    cnt = 0
    diff_cnt = 0
    with open(compare_txt, encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('/') + 1:]
            vin = split_res[1].strip()
            image_vin[image_name] = vin

    image_list = get_image_file_list(img_dir)
    for img in image_list:
        print(cnt, "-------total")
        cnt += 1
        img_name = img[img.rfind('\\') + 1:]
        try:
            with open(img, 'rb') as file:
                image = file.read()
            image = base64.b64encode(image).decode()
            data = {"key": ["image", "cls"], "value": [image, "5000"]}
            r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 15))
            vin = r.json()['value'][0][2:19]
            if image_vin[img_name] != vin:
                res_list.append(img + " " + image_vin[img_name] + " " + vin)
                diff_cnt += 1
                print(diff_cnt, "-------diff_total")
        except Exception as e:
            print("error --- > ", e)

    write_str_list_to_txt(res_list, res_txt_path)


def compare_single(res_list, image_vin, vin_ocr_url, img):
    img_name = img[img.rfind('\\') + 1:]
    try:
        with open(img, 'rb') as file:
            image = file.read()
        image = base64.b64encode(image).decode()
        data = {"key": ["image", "expect_cls"], "value": [image, "V"]}
        r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 150))
        vin = r.json()['value'][0][2:19]
        if image_vin[img_name] != vin:
            res_list.append(img + " " + image_vin[img_name] + " " + vin)
    except Exception as e:
        print("error --- > ", e)
        print(img)


def compare_vin_parallel(img_dir, compare_txt, res_txt_path):
    res_list = []
    image_vin = {}
    vin_ocr_url = "http://192.168.60.30:9998/ocr/prediction"

    with open(compare_txt, encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('/') + 1:]
            vin = split_res[1].strip()
            image_vin[image_name] = vin

    image_list = get_image_file_list(img_dir)

    pfunc = partial(compare_single, res_list, image_vin, vin_ocr_url)
    parallel_process(pfunc, image_list)

    write_str_list_to_txt(res_list, res_txt_path)

def compare_vin_yitu_online(img_dir, res_txt_path):
    res_list = []
    vin_ocr_url = "http://192.168.70.36:9998/ocr/prediction"
    yitu_ocr_url = "http://172.16.20.205/OcrWeb/servlet/OcrServlet"

    cnt = 0
    diff_cnt = 0

    cjml_time_all = 0
    yitu_time_all = 0
    image_list = get_image_file_list(img_dir)
    for img in image_list:
        print(cnt, "-------total")
        cnt += 1

        try:
            with open(img, 'rb') as file:
                image = file.read()
            image = base64.b64encode(image).decode()
            data = {"key": ["image", "cls"], "value": [image, "5000"]}

            time_start = time.time()
            r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 15))
            time_end = time.time()
            cjml_time_all = cjml_time_all + (time_end - time_start)
            print(time_end - time_start)

            vin = r.json()['value'][0][2:19]

            yitu_data = urlencode({"filedata": image, "pid": "1"})
            head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
            # data = {"key": ["image", "cls"], "value": [image, "5000"]}
            # print(json.dumps(data))
            yitu_time_start = time.time()
            yitu_r = requests.post(url=yitu_ocr_url, timeout=(5, 30), headers=head, data=yitu_data)
            yitu_time_end = time.time()
            yitu_time_all = yitu_time_all + (yitu_time_end - yitu_time_start)
            print(yitu_time_end - yitu_time_start)

            if int(yitu_r.json()['ErrorCode']) != 0 or vin == '':
                res_list.append(img + " " + "None" + " " + vin)
                diff_cnt += 1
                print(diff_cnt, "-------diff_total")
            elif yitu_r.json()['VIN'] != vin:
                print(yitu_r.json()['VIN'], "---", vin)
                res_list.append(img + " " + yitu_r.json()['VIN'] + " " + vin)
                diff_cnt += 1
                print(diff_cnt, "-------diff_total")
        except Exception as e:
            print("error --- > ", e)

    write_str_list_to_txt(res_list, res_txt_path)
    print(cjml_time_all, "------", yitu_time_all)


def compare_vin_yitu2_online(img_dir, res_txt_path):
    res_list = []

    yitu_old_ocr_url = "http://172.16.20.205/OcrWeb/servlet/OcrServlet"

    yitu_ocr_url = "http://172.16.30.140:8080/OcrWeb/servlet/OcrServlet"

    cnt = 0
    diff_cnt = 0

    yitu_old_time_all = 0
    yitu_time_all = 0
    image_list = get_image_file_list(img_dir)
    for img in image_list:
        print(cnt, "-------total")
        cnt += 1

        try:
            with open(img, 'rb') as file:
                image = file.read()
            image = base64.b64encode(image).decode()

            yitu_data_old = urlencode({"filedata": image, "pid": "1"})
            head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
            # data = {"key": ["image", "cls"], "value": [image, "5000"]}
            # print(json.dumps(data))
            yitu_old_time_start = time.time()
            yitu_old_r = requests.post(url=yitu_old_ocr_url, timeout=(5, 30), headers=head, data=yitu_data_old)
            yitu_old_time_end = time.time()
            yitu_old_time_all = yitu_old_time_all + (yitu_old_time_end - yitu_old_time_start)
            print(yitu_old_time_end - yitu_old_time_start)

            yitu_data = urlencode({"filedata": image, "pid": "1"})
            head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
            # data = {"key": ["image", "cls"], "value": [image, "5000"]}
            # print(json.dumps(data))
            yitu_time_start = time.time()
            yitu_r = requests.post(url=yitu_ocr_url, timeout=(5, 30), headers=head, data=yitu_data)
            yitu_time_end = time.time()
            yitu_time_all = yitu_time_all + (yitu_time_end - yitu_time_start)
            print(yitu_time_end - yitu_time_start)

            if int(yitu_r.json()['ErrorCode']) != 0 or int(yitu_old_r.json()['ErrorCode']) != 0:
                # old = "None" if int(yitu_r.json()['ErrorCode']) != 0 else yitu_r.json()['VIN']
                old = ("None", yitu_old_r.json()['VIN'])[int(yitu_old_r.json()['ErrorCode']) == 0]
                new = ("None", yitu_r.json()['VIN'])[int(yitu_r.json()['ErrorCode']) == 0]
                res_list.append(img + " " + old + " " + new)
                diff_cnt += 1
                print(diff_cnt, "-------diff_total")
            elif yitu_r.json()['VIN'] != yitu_old_r.json()['VIN']:
                print(yitu_r.json()['VIN'], "---", yitu_old_r.json()['VIN'])
                res_list.append(img + " " + yitu_old_r.json()['VIN'] + " " + yitu_r.json()['VIN'])
                diff_cnt += 1
                print(diff_cnt, "-------diff_total")
        except Exception as e:
            print("error --- > ", e)

    write_str_list_to_txt(res_list, res_txt_path)
    print(yitu_old_time_all, "------", yitu_time_all)


def start_vis_diff():
    im_dir = 'D:/vin_eval_5k'
    res_txt = 'diff_eval_5k_big_new.txt'
    compare_txt = "20220829_vin_url.txt"
    compare_vin_parallel(im_dir, compare_txt, res_txt)
    # compare_vin_yitu_online(im_dir, res_txt)
    # compare_vin_yitu2_online(im_dir, res_txt)
    diff_im_dir = 'D:/diff_vin_eval_5k_big_new/'
    visual_diff_vin(txt_path=res_txt, save_dir=diff_im_dir)


def gain_diff_img(img_dir, des_dir, sum_im):
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)
    cnt = [0, 0]
    image_vin = {}
    vin_ocr_url = "http://192.168.60.30:9998/ocr/prediction"
    with open("20220915_vin_url.txt", encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('/') + 1:]
            vin = split_res[1].strip()
            image_vin[image_name] = vin

    image_list = get_image_file_list(img_dir)

    pfunc = partial(single_diff, cnt, sum_im, vin_ocr_url, image_vin, des_dir)
    parallel_process(pfunc, image_list)

    print("sum: --------->", cnt[0])


def single_diff(cnt, sum_im, vin_ocr_url, image_vin, des_dir, img):
    img_name = img[img.rfind('\\') + 1:]
    cnt[0] += 1
    print("now cnt -------------->", cnt[0])
    if cnt[0] > sum_im:
        return
    try:
        with open(img, 'rb') as file:
            image = file.read()
        image = base64.b64encode(image).decode()
        data = {"key": ["image", "expect_cls"], "value": [image, "V"]}
        r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 15))
        vin = r.json()['value'][0][2:19]
        if image_vin[img_name] != vin:
            shutil.move(img, des_dir)
            cnt[1] += 1
            print("diff cnt -------------->", cnt[1])
        else:
            os.remove(img)
    except Exception as e:
        print("error --- > ", e)
        print(img)


if __name__ == '__main__':
    # start_vis_diff()
    dir1 = "D:\\vin_scan_imgs"
    dir2 = "D:\\vin_scan_imgs_diff"
    cnt = 99999999
    gain_diff_img(dir1, dir2, cnt)

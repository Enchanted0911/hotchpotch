import base64
import json
import time
from functools import partial
from urllib.parse import urlencode

import cv2
import requests

from cjml_utils.file_util import get_image_file_list, write_str_list_to_txt
from cjml_utils.parallel_util import parallel_process
from cjml_utils.visual_error import visual_diff_vin


def get_predict_by_yitu(img_dir, res_txt_path, ocr_url):
    res_list = []
    image_list = get_image_file_list(img_dir)
    pfunc = partial(yitu_single, res_list, ocr_url)
    parallel_process(pfunc, image_list)
    write_str_list_to_txt(res_list, res_txt_path)


def get_predict_by_strange(img_dir, res_txt_path, ocr_url):
    res_list = []

    image_list = get_image_file_list(img_dir)

    pfunc = partial(strange_single, res_list, ocr_url)
    parallel_process(pfunc, image_list)
    write_str_list_to_txt(res_list, res_txt_path)


def strange_single(res_list, vin_ocr_url, img):
    try:
        with open(img, 'rb') as file:
            image = file.read()
        # image = cv2.imread(img)
        #
        # image_base64_str = cv2.imencode('.jpg', image)[1].tobytes()
        # image = base64.b64encode(image_base64_str).decode('utf8')

        image = base64.b64encode(image).decode()
        data = {"key": ["image", "expect_cls"], "value": [image, "V"]}
        strange_time_start = time.time()
        r = requests.post(url=vin_ocr_url, data=json.dumps(data), timeout=(5, 150))
        strange_time_end = time.time()
        print(strange_time_end - strange_time_start)
        vin = r.json()['value'][0][2:19]
        res_list.append(img + " " + vin)
    except Exception as e:
        print("error --- > ", e)
        print(img)


def yitu_single(res_list, vin_ocr_url, img):
    try:
        with open(img, 'rb') as file:
            image = file.read()
        image = base64.b64encode(image).decode()
        yitu_data = urlencode({"filedata": image, "pid": "1"})
        head = {"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", 'Connection': 'close'}
        yitu_time_start = time.time()
        yitu_r = requests.post(url=vin_ocr_url, timeout=(5, 30), headers=head, data=yitu_data)
        yitu_time_end = time.time()
        print(yitu_time_end - yitu_time_start)
        vin = ("None", yitu_r.json()['VIN'])[int(yitu_r.json()['ErrorCode']) == 0]
        res_list.append(img + " " + vin)

    except Exception as e:
        print("error --- > ", e)
        print(img)


def compare_by_res_txt(one_res, two_res, diff_res_path, diff_im_dir):
    res_list = []
    image_vin = {}
    with open(one_res, encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('\\') + 1:]
            vin = split_res[1].strip()
            image_vin[image_name] = vin

    with open(two_res, encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('\\') + 1:]
            vin = split_res[1].strip()
            if image_name in image_vin.keys():
                if image_vin[image_name] != vin:
                    res_list.append(image_path + " " + image_vin[image_name] + " " + vin)

    print("acc -------->", 1 - len(res_list) / len(image_vin), len(res_list), len(image_vin))
    write_str_list_to_txt(res_list, diff_res_path)
    visual_diff_vin(txt_path=diff_res_path, save_dir=diff_im_dir)



img_dir = r"D:\eval_1k_normal_pic"
img_dir_3000 = r"D:\wjs\clas_data_set\train_data\3000"
img_dir_7k = r"D:\vin_scan_imgs_diff"
stable = r"D:\eval_1k_normal_pic_res\stable.txt"
res_txt_yitu = r"D:\eval_1k_normal_pic_res\yitu.txt"
res_txt_yitu_3000 = r"D:\eval_1k_normal_pic_res\yitu_3000.txt"
res_txt_yitu_7k = r"D:\eval_1k_normal_pic_res\yitu_7k.txt"
res_txt_strange = r"D:\eval_1k_normal_pic_res\strange.txt"
res_txt_strange_temp = r"D:\eval_1k_normal_pic_res\strange_temp.txt"
res_txt_strange_3000 = r"D:\eval_1k_normal_pic_res\strange_3000.txt"
res_txt_strange_7k = r"D:\eval_1k_normal_pic_res\strange_7k.txt"
yitu_new_ocr_url = "http://172.16.30.140:8080/OcrWeb/servlet/OcrServlet"
yitu_old_ocr_url = "http://172.16.20.205/OcrWeb/servlet/OcrServlet"
strange_ocr_url = "http://192.168.70.21:9998/ocr/prediction"
strange_ocr_url_1 = "http://192.168.60.30:9998/ocr/prediction"
strange_ocr_url_2 = "http://192.168.70.36:9998/ocr/prediction"
strange_ocr_url_3 = "http://121.196.210.106:9998/ocr/prediction"
diff_res_path = r"D:\eval_1k_normal_pic_res\err_strange.txt"
diff_im_dir = "D:/eval_1k_normal_pic_res/err_strange/"
diff_res_path_temp = r"D:\eval_1k_normal_pic_res\err_strange_temp.txt"
diff_im_dir_temp = "D:/eval_1k_normal_pic_res/err_strange_temp/"
diff_res_path_2k = r"D:\eval_2k_normal_pic_res\diff_strange.txt"
diff_im_dir_2k = "D:/eval_2k_normal_pic_res/diff_strange/"


if __name__ == '__main__':
    # get_predict_by_yitu(img_dir_7k, res_txt_yitu_7k, yitu_old_ocr_url)
    # get_predict_by_strange(img_dir, res_txt_strange_prod, strange_ocr_url_1)
    get_predict_by_strange(img_dir, res_txt_strange_temp, strange_ocr_url_2)
    # get_predict_by_strange(img_dir_3000, res_txt_strange_3000, strange_ocr_url_1)
    compare_by_res_txt(stable, res_txt_strange_temp, diff_res_path_temp, diff_im_dir_temp)
    # compare_by_res_txt(res_txt_yitu_3000, res_txt_strange_3000, diff_res_path_2k, diff_im_dir_2k)
    # compare_by_res_txt(stable, res_txt_yitu, diff_res_path, diff_im_dir)

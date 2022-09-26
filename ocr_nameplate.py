import base64
import json
import os
import time
from ast import literal_eval
from functools import partial

import cv2
import requests

from paddle4cjml.cjml_clas import CjmlClas
from paddle4cjml.cjml_detection import CjmlDetection
from paddle4cjml.cjml_ocr import *
from evaluation import *
from fetch_data_from_db import parallel_process
import math

from cjml_utils.box_util import gain_angle_by_add_det
from cjml_utils.file_util import fetch_label_text_content, txt_dict2dict
from cjml_utils.img_util import rotate_image, rotate_right_image

det_model_dir = 'infer_first_1k_it6/det'
rec_model_dir = 'infer_first_1k_it6/rec'
cls_model_dir = 'infer_first_1k_it6/cls'

rec_char_dict_path = 'dict/ppocr_keys_v1.txt'


def start_ocr_eval_by_image(image_dir_slope, image_dir_all, label_path):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}

    standard_label = fetch_label_text_content(label_path)

    ocr = CjmlOcr(model_args)
    res_slope = ocr.ocr(image_dir_slope)

    res_all = ocr.ocr(image_dir_all)

    process_real_dict(standard_label)
    res_slope_score, list_slope_res = eval_ocr(res_slope, standard_label)
    res_all_score, list_all_res = eval_ocr(res_all, standard_label)

    # print(len(set(list_one) & set(list_two)))
    # for s in set(list_one) - set(list_two):
    #     oldpath = 'no_det\\'
    #     newpath = 'nice_no_det\\'
    #     if os.path.exists(oldpath + s):
    #         shutil.copy(oldpath + s, newpath + s)
    print(res_slope_score, res_all_score)


def start_ocr_eval_online(image_dir, label_path):
    standard_label = fetch_label_text_content(label_path)

    result = {}
    image_list = get_image_file_list(image_dir)
    pfunc = partial(process_online_ocr_one, result)
    parallel_process(pfunc, image_list)
    process_real_dict(standard_label)
    res_all_score, list_all_res = eval_ocr(result, standard_label)
    print(res_all_score)


def process_online_ocr_one(result, image_path):
    # ocr_url = "http://172.16.30.125:9998/ocr/prediction"
    ocr_url = "http://192.168.60.30:9998/ocr/prediction"
    with open(image_path, 'rb') as file:
        image = file.read()
    image = base64.b64encode(image).decode()
    # data = {"key": ["image", "mode"], "value": [image, "011"]}
    data = {"key": ["image", "mode"], "value": [image, "XXX"]}

    time_start = time.time()
    r = requests.post(url=ocr_url, data=json.dumps(data), timeout=(5, 15))
    time_end = time.time()
    print(time_end - time_start)

    res = literal_eval(r.json()['value'][0])
    print(res)
    image_name = image_path[image_path.rfind('\\') + 1:]
    result[image_name] = res


def start_ocr_eval_by_image_single(image_dir_all, label_path):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}

    standard_label = fetch_label_text_content(label_path)

    ocr = CjmlOcr(model_args)

    res_all = ocr.ocr(image_dir_all)

    process_real_dict(standard_label)
    res_all_score, list_all_res = eval_ocr(res_all, standard_label)
    print(res_all_score)


def start_ocr_eval_by_predict_label(predict_slope_path, predict_all_path, label_path):
    standard_label = fetch_label_text_content(label_path)

    res_all = txt_dict2dict(predict_all_path)
    res_slope = txt_dict2dict(predict_slope_path)
    process_real_dict(standard_label)
    res_slope_score, list_slope_res = eval_ocr(res_slope, standard_label)
    res_all_score, list_all_res = eval_ocr(res_all, standard_label)
    print(res_slope_score, res_all_score)


def generate_det_res_add_det(no_clas_dir
                             , no_det_dir
                             , add_det_all_dir
                             , all_det_des_dir
                             , rotate_supply_dir
                             , no_right_det_dir
                             , crop_dir
                             ):
    if not os.path.exists(no_det_dir):
        os.makedirs(no_det_dir)
    if not os.path.exists(rotate_supply_dir):
        os.makedirs(rotate_supply_dir)
    if not os.path.exists(all_det_des_dir):
        os.makedirs(all_det_des_dir)
    if not os.path.exists(no_right_det_dir):
        os.makedirs(no_right_det_dir)
    if not os.path.exists(add_det_all_dir):
        os.makedirs(add_det_all_dir)
    if not os.path.exists(crop_dir):
        os.makedirs(crop_dir)

    image_path_list = get_image_file_list(no_clas_dir)
    det = CjmlDetection()
    clas = CjmlClas(top_k=2)

    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
    ocr = CjmlOcr(model_args)

    for i in image_path_list:
        if i[-5: -4] == '本':
            continue
        class_and_score_res_list = clas.get_image_top2_class_and_score(i)
        top_1_class = class_and_score_res_list[0][0]

        angle = top_1_class % 1000
        rotated_img, rotated_img_path = rotate_image(i, no_det_dir, angle)
        if top_1_class // 1000 != 5 and top_1_class // 1000 != 2:
            if angle % 10 != 0 or top_1_class // 1000 == 3:
                location, category_id = det.get_location_and_category_id(rotated_img_path)
                location = [int(f) for f in location]
                det_img = rotated_img[location[1]: location[1] + location[3], location[0]: location[0] + location[2]]
                cv2.imwrite(all_det_des_dir + i[i.rfind('\\') + 1:], det_img)
            else:
                rotated_right_img, rotated_right_img_path = rotate_right_image(rotated_img_path, no_right_det_dir)
                location, category_id = det.get_location_and_category_id(rotated_right_img_path)
                location = [int(f) for f in location]
                det_right_img = rotated_right_img[location[1]: location[1] + location[3],
                                location[0]: location[0] + location[2]]
                cv2.imwrite(all_det_des_dir + i[i.rfind('\\') + 1:], det_right_img)
        else:
            cv2.imwrite(all_det_des_dir + i[i.rfind('\\') + 1:], rotated_img)

        i = all_det_des_dir + i[i.rfind('\\') + 1:]

        add_det_all_det_res = list(ocr.ocr(i, rec=False).values())[0]

        flag, add_det_all_det_angle = gain_angle_by_add_det(add_det_all_det_res)
        add_det_img, add_det_img_path = rotate_image(i, add_det_all_dir, add_det_all_det_angle)
        new_i = crop_dir + i[i.rfind('\\') + 1:]
        if flag:
            cv2.imwrite(new_i, add_det_img)
            continue
        width = cv2.imread(i).shape[1]
        add_det_height = add_det_img.shape[0]
        crop_len = int(width * math.sin(abs(add_det_all_det_angle) / 180 * math.pi) / 2)
        crop_img = add_det_img[crop_len: add_det_height - crop_len, :]
        cv2.imwrite(new_i, crop_img)


def start_eval_add_det():
    no_clas = 'D:\\wjs\\PycharmProjects\\static\\pic\\download_image\\'
    no_det = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\no_det\\'
    all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\all_det_des\\'
    no_right_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\no_right_det_des\\'
    add_det_all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\add_det_all_det_des\\'
    rotate_supply_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\rotate_supply_des\\'
    crop_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\eval_e1_it6_add_det_plus\\crop_des\\'
    # generate_det_res_add_det_plus(no_clas, no_det, add_det_all_det_des, all_det_des, rotate_supply_des, no_right_det_des, crop_des)
    start_ocr_eval_by_image_single(crop_des, 'Label.txt')


def start_eval_add_det_hard():
    no_clas = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_1\\'
    no_det = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\no_det\\'
    all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\all_det_des\\'
    no_right_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\no_right_det_des\\'
    add_det_all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\add_det_all_det_des\\'
    rotate_supply_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\rotate_supply_des\\'
    crop_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\crop_des\\'
    # generate_det_res_add_det_plus(no_clas, no_det, add_det_all_det_des, all_det_des, rotate_supply_des, no_right_det_des, crop_des)
    start_ocr_eval_by_image_single(crop_des, 'Label_hard.txt')


def generate_new():
    no_clas = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin'
    no_det = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\no_det\\'
    all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\all_det_des\\'
    no_right_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\no_right_det_des\\'
    add_det_all_det_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\add_det_all_det_des\\'
    rotate_supply_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\rotate_supply_des\\'
    crop_des = 'D:\\wjs\\PycharmProjects\\static\\pic\\temp_vin\\crop_des\\'
    generate_det_res_add_det(no_clas, no_det, add_det_all_det_des, all_det_des, rotate_supply_des, no_right_det_des,
                             crop_des)


def start_eval_hard_online():
    # eval_dir = 'D:\\wjs\\PycharmProjects\\static\\pic\\download_image\\'
    eval_dir = 'D:\\wjs\\PycharmProjects\\static\\pic\\200difficult_res\\no_det\\'
    start_ocr_eval_online(eval_dir, 'Label_hard.txt')


def start_eval_online():
    eval_dir = 'D:\\wjs\\PycharmProjects\\static\\pic\\download_image\\'
    start_ocr_eval_online(eval_dir, 'Label.txt')


if __name__ == '__main__':
    # start_eval_hard_online()
    # start_eval_online()
    # start_eval_add_det()
    start_eval_add_det_hard()
    # print(multiprocessing.cpu_count())
    # generate_new()



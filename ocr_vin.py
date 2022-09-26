import os

import cv2
import imutils

from decode_vin.vin_alpha import alpha_type
from paddle4cjml.cjml_ocr import *
from cjml_utils.box_util import gain_angle_by_add_det, gain_lr_bound
from cjml_utils.file_util import get_image_file_list, write_str_list_to_txt
from cjml_utils.img_util import rotate_image, normalize_img
from cjml_utils.visual_error import visual_diff_vin

det_model_dir = 'infer4vin/det'
rec_model_dir = 'infer4vin/rec'
cls_model_dir = 'infer4vin/cls'

rec_char_dict_path = 'dict/ppocr_keys_v1.txt'


def start_diff_vin(img_dir, res_txt_path, diff_im_dir):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}

    ocr = CjmlOcr(model_args)

    res_list = []
    image_vin = {}
    with open("20220705_vin_url.txt", encoding='utf-8') as lines:
        for line in lines:
            split_res = line.split(' ')
            if len(split_res) < 2:
                continue
            image_path = split_res[0]
            image_name = image_path[image_path.rfind('/') + 1:]
            vin = split_res[1].strip()
            image_vin[image_name] = vin

    ocr_res = ocr.ocr(img_dir)

    for k, v in ocr_res.items():
        vin = alpha_type(v)
        if image_vin[k] != vin['res']:
            res_list.append(img_dir + k + " " + image_vin[k] + " " + vin['res'])

    print("diff_num: -------------->" + str(len(res_list)))
    write_str_list_to_txt(res_list, res_txt_path)
    visual_diff_vin(txt_path=res_txt_path, save_dir=diff_im_dir)


def vin_ocr_res(img_dir):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}

    ocr = CjmlOcr(model_args)

    ocr_res = ocr.ocr(img_dir)

    print(ocr_res)


def generate_vin_pre_process(origin_dir, pre_det_dir, des_dir):
    if not os.path.exists(pre_det_dir):
        os.makedirs(pre_det_dir)
    if not os.path.exists(des_dir):
        os.makedirs(des_dir)

    image_path_list = get_image_file_list(origin_dir)

    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
        , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
    ocr = CjmlOcr(model_args)

    for i in image_path_list:
        if i[-5: -4] == '本':
            continue

        im = cv2.imread(i)
        h, w, _ = im.shape
        if h > w:
            im, i = rotate_image(i, pre_det_dir, 270)
            h, w, _ = im.shape

        pre_det_res = list(ocr.ocr(i, rec=False).values())[0]

        if len(pre_det_res) > 0:
            l_bound, r_bound = gain_lr_bound(pre_det_res)
            if l_bound / w - 0.1 > 0 and r_bound / w - 0.9 < 0:
                im = im[:, int(l_bound / 3 * 2): int(r_bound + (w - r_bound) / 3)]

        flag, pre_det_angle = gain_angle_by_add_det(pre_det_res)
        # add_det_img, add_det_img_path = rotate_image(i, des_dir, pre_det_angle)
        im = imutils.rotate_bound(im, -1 * pre_det_angle)
        if pre_det_angle < 10:
            im = normalize_img(im)

        new_i = des_dir + i[i.rfind('\\') + 1:]
        cv2.imwrite(new_i, im)


def start_eval_add_det_num(num):
    origin_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\vin_' + num + '\\'
    pre_det_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\eval_vin_' + num + '\\pre_det_dir\\'
    des_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\eval_vin_' + num + '\\des_dir\\'
    generate_vin_pre_process(origin_dir, pre_det_dir, des_dir)
    diff_txt_path = 'diff_txt_vin_' + num + '.txt'
    diff_img_dir = 'pic/vis_diff_vin_' + num + '/'
    start_diff_vin(des_dir, diff_txt_path, diff_img_dir)


def start_eval_add_det():
    origin_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\vin_2k\\'
    pre_det_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\vin_2k\\pre_det_dir_1\\'
    des_dir = 'D:\\wjs\\PycharmProjects\\end2end_eval\\pic\\vin_2k\\des_dir_1\\'
    generate_vin_pre_process(origin_dir, pre_det_dir, des_dir)
    diff_txt_path = 'pic/vin_2k/diff_txt_only_vin_1.txt'
    diff_img_dir = 'pic/vin_2k/diff_txt_only_vin_1/'
    start_diff_vin(des_dir, diff_txt_path, diff_img_dir)


def start_eval_temp_err():
    origin_dir = 'D:/wjs/PycharmProjects/end2end_eval/pic/temp_err/'
    pre_det_dir = 'D:/wjs/PycharmProjects/end2end_eval/pic/eval_temp_err/pre_det_dir/'
    des_dir = 'D:/wjs/PycharmProjects/end2end_eval/pic/eval_temp_err/des_dir/'
    generate_vin_pre_process(origin_dir, pre_det_dir, des_dir)
    diff_txt_path = 'diff_txt_only_vin.txt'
    diff_img_dir = 'pic/diff_txt_only_vin/'
    # start_diff_vin(des_dir, diff_txt_path, diff_img_dir)
    vin_ocr_res(des_dir)


if __name__ == '__main__':
    # start_eval_add_det_num(str(2))
    # start_eval_add_det_num(str(0))
    # start_eval_add_det_num(str(3))
    # start_eval_add_det_num(str(4))
    # start_eval_temp_err()
    start_eval_add_det()

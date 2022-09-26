import os

import cv2
import imutils
from PIL import Image

from cjml_utils.file_util import get_dict_by_excel
from cjml_utils.img_util import generate_blank_image, mark_on_pic4vin, merge_two_pic, mark_on_pic


def visual_diff_vin(txt_path, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir + 'raw/')

    with open(txt_path, encoding='utf-8') as lines:
        for line in lines:
            try:
                split_res = line.split(' ')
                image_path = split_res[0]
                image_name = image_path[image_path.rfind('\\') + 1:]
                yitu_vin = split_res[1].strip()
                cjml_vin = "none"
                if len(split_res) == 3:
                    cjml_vin = split_res[2].strip()

                one_pic = cv2.imread(image_path)
                h, w, _ = one_pic.shape
                if h > w:
                    one_pic = imutils.rotate_bound(one_pic, 90)
                    h, w, _ = one_pic.shape
                blank_img = generate_blank_image((w, h))
                two_pic = mark_on_pic4vin(["译图: " + yitu_vin, "cjml: " + cjml_vin], blank_img)
                pic = merge_two_pic(one_pic, two_pic)
                cv2.imwrite(save_dir + image_name, pic)
                cv2.imwrite(save_dir + 'raw/' + image_name, one_pic)
            except Exception as e:
                print("err", e, line)


def old_vis():
    img_dict = get_dict_by_excel('error.xlsx', 'alldet')
    for k, v in img_dict.items():
        one_pic = Image.open(
            'wrong_alldet_res/' + k)
        blank_img = generate_blank_image(one_pic.size)
        two_pic = mark_on_pic(v, blank_img)
        pic = merge_two_pic(one_pic, two_pic)
        cv2.imwrite('wrong_alldet_compare/' + k, pic)


if __name__ == '__main__':
    pass

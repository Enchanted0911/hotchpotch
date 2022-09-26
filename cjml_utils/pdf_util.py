import json
import os

import pdfplumber
from fitz import fitz

from paddle4cjml.cjml_ocr import CjmlOcr


def get_text(pdf_path, pdf_pages):
    with pdfplumber.open(pdf_path) as pdf:
        for page_num in pdf_pages:
            page = pdf.pages[page_num]
            text = page.extract_text()
            print(page_num)
            with open("page" + str(page_num) + ".txt", 'a', encoding='utf-8') as p:
                p.writelines(text)


def pdf2img(pdf_path, pdf_res=None):
    if not pdf_path[-4:] == '.pdf' and not pdf_path[-4:] == '.PDF':
        print("not pdf file :", pdf_path)

    if pdf_res == None:
        pdf_res = pdf_path[:-4]

    pdf_name = pdf_path.split('/')[-1][: -4]

    pdf_doc = fitz.open(pdf_path)

    for pg in range(pdf_doc.page_count):

        imageName = pdf_res + '/' + pdf_name + '_' + str(pg) + '.jpg'

        page = pdf_doc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=96
        zoom_x = 1.3  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.3
        mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        if not os.path.exists(pdf_res):  # 判断存放图片的文件夹是否存在
            os.makedirs(pdf_res)  # 若图片文件夹不存在就创建

        # imageName = imagePath.split('\\')[-1] + "_" + str(pg) + ".jpg"
        if not os.path.exists(imageName):
            pix.save(imageName)  # 将图片写入指定的文件夹内
    if pdf_doc.page_count < 1:
        print("打开文件为空")


def generate4json():
    pdf_root = r'D:/pdf4dingc'
    pdf_list = os.listdir(pdf_root)
    for pdf in pdf_list:
        print(pdf)
        if pdf[-4:] != '.pdf' and pdf[-4:] != '.PDF' or '刹车盘,制动片组件.pdf' in pdf or '刹车蹄,刹车鼓,驻车刹车蹄.pdf' in pdf:
            continue
        pdf_path = pdf_root + "/" + pdf
        print(pdf_path)
        pdf2img(pdf_path)
        res = ocr.ocr(pdf_path[: -4], use_decode=False, use_location=True)
        res = json.dumps(res)
        with open(pdf_path[: -4] + ".json", 'a', encoding='utf-8') as p:
            p.write(res)


det_model_dir = '../ocr_infer/det'
rec_model_dir = '../ocr_infer/rec'
cls_model_dir = '../ocr_infer/cls'

rec_char_dict_path = '../dict/ppocr_keys_v1.txt'
model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
    , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
ocr = CjmlOcr(model_args)

if __name__ == '__main__':
    # pdf_path = r'C:\Users\wujs.YANGCHE\Desktop\刹车盘,制动片组件.pdf'
    # get_text(pdf_path, range(1, 3))
    # res = ocr.ocr('../temp_pic', use_decode=False, use_location=True)
    # res = json.dumps(res)
    # with open("temp_pic.json", 'a', encoding='utf-8') as p:
    #     p.write(res)
    generate4json()

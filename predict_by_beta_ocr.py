import base64
import json
import shutil

import pymysql
import requests

from fetch_data_from_db import parallel_process
from file_process import get_image_file_list
from cjml_utils.img_util import download_img

conn = pymysql.connect(
    host='192.168.60.30',
    port=3306,
    user='wujs2',
    password='Vinplate!999',
    db='nameplate',
    charset='utf8'
)
save_failed_dir = "parallel_failed/"
url_head = "http://192.168.88.6:9000/vin-plates/"
ocr_service_url = 'http://192.168.70.20:9899/predict'
alpha_ocr_service_url = "http://192.168.70.21:9998/ocr/prediction"
identification_service_url = "http://192.168.100.51:60209/service_vin/test/testanalyzevinbynameplate"
succ_sum = []
succ_image = []
total_sum = []


def fetch_failed_img_url():
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    # sql = "SELECT filePath FROM nameplate_raw WHERE createdAt between '2021-12-20' and '2022-06-20' AND cls = " + str(angle) + " AND conclusion like '%mmu%' ORDER BY createdAt DESC LIMIT " + str(nums)
    sql = "SELECT filePath FROM nameplate_raw WHERE createdAt between '2022-06-13' and '2022-06-14' AND cls > 3999 AND conclusion not like '%mmu%'"
    # 执行sql语句
    cursor.execute(sql)
    sql_res = cursor.fetchall()
    img_url_res_list = [url_head + r['filePath'] for r in sql_res]
    return img_url_res_list


def process_failed(path):
    global succ_sum
    try:
        download_img(save_failed_dir, path)
        succ_sum += 1
        print(succ_sum)
    except Exception as e:
        print("error img", e)
        return


def process_ocr_text(ocr_text):
    lines = []
    for line in ocr_text[1:-1].split(','):
        lines.append(line.replace('"', '').replace("'", ''))

    return lines


def alpha_ocr_predict(image_path):
    with open(image_path, 'rb') as file:
        next_image = file.read()
        image = base64.b64encode(next_image).decode('utf8')

    data = {"key": ["image"], "value": [image]}
    r = requests.post(url=alpha_ocr_service_url, data=json.dumps(data), timeout=(5, 15))
    jresult = r.json()

    lines = process_ocr_text(jresult['value'][0])
    return lines


def ocr_predict(image_path):
    with open(image_path, 'rb') as file:
        image = file.read()
    file = {"img": ("file_name.jpg", image, "image/jpg")}
    r = requests.post(url=ocr_service_url, files=file, timeout=(5, 15))
    ocr_text = []
    try:
        ocr_text = r.json()
    except Exception as e:
        print("request error!!!", e)
    return ocr_text


def identify_mmu1(lines):
    try:
        data = {"nameplateWords": lines}
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        r = requests.post(url=identification_service_url, data=json.dumps(data), headers=headers)
        jresult = r.json()
        if jresult['status'] == 0:
            vinCode = ''
            if jresult['result']['analyzeNameplateTextResponse']['vinCode'] is not None:
                vinCode = jresult['result']['analyzeNameplateTextResponse']['vinCode']
            mmu1Id = 0
            if jresult['result']['autoInfo'] is not None:
                mmu1Id = jresult['result']['autoInfo']['mmuOneId']
            conclusion = jresult['result']['conclusion']
            # print('vinCode=', vinCode, '  mmu1Id=', mmu1Id, '  conclusion=', conclusion)
            return vinCode.upper(), mmu1Id, conclusion
    except Exception as e:
        print('filed to identify the nameplate.', e)

    return '', '', ''


def batch_ocr_predict_vin(ocr_dir):
    image_path_list = get_image_file_list(ocr_dir)
    parallel_process(process_ocr_vin, image_path_list)
    print(len(succ_sum))
    with open('succ_images_old.txt', 'a+', encoding='utf-8') as f:
        for data in succ_image:
            f.write(data + '\n')
        f.close()


def process_ocr_vin(image_path):
    # ocr_text = ocr_predict(image_path)
    ocr_text = alpha_ocr_predict(image_path)
    (vinCode, mmu1Id, conclusion) = identify_mmu1(ocr_text)
    if 'mmu' in conclusion:
        succ_sum.append(1)
        succ_image.append(image_path + ' ' + vinCode + ' ' + conclusion)
        shutil.move(image_path, './succ_imgs_old/')
        print(len(succ_sum))
    total_sum.append(1)
    if len(total_sum) % 50 == 0:
        print(len(total_sum))


if __name__ == '__main__':
    # parallel_process(process_failed, fetch_failed_img_url())
    o_dir = './succ_imgs'
    batch_ocr_predict_vin(o_dir)

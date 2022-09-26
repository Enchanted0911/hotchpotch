import multiprocessing.dummy as parallel
import os

import pymysql

from cjml_utils.img_util import download_img

conn = pymysql.connect(
    host='192.168.60.30',
    port=3306,
    user='wujs2',
    password='Vinplate!999',
    db='nameplate',
    charset='utf8'
)
size = 5000
cls_angle = 4315
save_clas_dir = "parallel_clas/" + str(cls_angle) + "/"
url_head = "http://192.168.88.6:9000/vin-plates/"
succ_sum = 0


def fetch_clas_img_url(angle, nums):
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # sql = "SELECT filePath FROM nameplate_raw WHERE createdAt between '2021-12-20' and '2022-06-20' AND cls = " + str(angle) + " AND conclusion like '%mmu%' ORDER BY createdAt DESC LIMIT " + str(nums)
    sql = "SELECT filePath FROM nameplate_raw WHERE createdAt between '2021-06-20' and '2022-06-24' AND cls = " \
          + str(angle) + " AND conclusion like '%mmu%' ORDER BY createdAt DESC LIMIT " + str(nums)
    # 执行sql语句
    cursor.execute(sql)
    sql_res = cursor.fetchall()
    img_url_res_list = [url_head + r['filePath'] for r in sql_res]
    return img_url_res_list


def parallel_process(process, path_list):
    pool = parallel.Pool(12)
    pool.map(process, path_list)
    pool.close()
    pool.join()


def process_clas(path):
    global succ_sum
    try:
        download_img(save_clas_dir, path)
        succ_sum += 1
        print(succ_sum)
    except Exception as e:
        print("error img")
        return


if __name__ == '__main__':
    if not os.path.exists(save_clas_dir):
        os.makedirs(save_clas_dir)
    res = fetch_clas_img_url(cls_angle, size)
    parallel_process(process_clas, res)

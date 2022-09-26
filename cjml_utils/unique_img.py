import hashlib
import os
import time


def getmd5(filename):
    """
    获取文件的md5值
    :param filename: 待获取的文件路径
    :return: 文件md5值
    """
    file_txt = open(filename, 'rb').read()
    m = hashlib.md5()
    m.update(file_txt)
    return m.hexdigest()


def unique(files_path):
    """
    去除目录下内容相同的文件
    :param files_path: 待处理的文件夹
    :return:
    """
    all_md5 = []
    total_file = 0
    total_delete = 0
    start = time.time()
    for file in os.listdir(files_path):
        total_file += 1
        real_path = os.path.join(files_path, file)
        if os.path.isfile(real_path):
            filemd5 = getmd5(real_path)
            if filemd5 in all_md5:
                total_delete += 1
                os.remove(real_path)
                print(u'删除', file)
            else:
                all_md5.append(filemd5)
    print(u'文件总数：', total_file)
    print(u'删除个数：', total_delete)
    print(u'耗时：', time.time() - start, u'秒')


if __name__ == '__main__':
    img_dir = r"D:\vin_scan_imgs_diff"
    unique(img_dir)

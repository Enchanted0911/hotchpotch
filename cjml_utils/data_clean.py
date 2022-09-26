import os.path
import shutil

from cjml_utils.file_util import get_image_file_list
from paddle4cjml.cjml_clas import CjmlClas


class DataClean:
    """
    数据清洗
    """
    def __init__(self, predictor):
        self.predictor = predictor

    def clean_clas(self, dir_path, stable_res):
        """
        清洗错误分类的数据，错误的数据将被移至新文件夹
        :param dir_path: 待清洗的目录
        :param stable_res: 期望该目录的分类结果
        :return:
        """
        image_path_list = get_image_file_list(dir_path)
        error_dir_path = dir_path + '_error'
        if not os.path.exists(error_dir_path):
            os.makedirs(error_dir_path)
        error_path_list = filter(lambda x: self.predictor.get_image_class(x) != stable_res, image_path_list)
        for e in error_path_list:
            shutil.move(e, error_dir_path)

    def auto_clas(self, dir_path):
        """
        对一个文件夹下的所有图片进行自动分类
        :param dir_path: 待分类的文件夹
        :return:
        """
        image_path_list = get_image_file_list(dir_path)
        for i in image_path_list:
            clas_res = self.predictor.get_image_class(i)
            clas_res_dir = dir_path + "\\" + str(clas_res)
            if not os.path.exists(clas_res_dir):
                os.makedirs(clas_res_dir)
            shutil.move(i, clas_res_dir)


def clean():
    clas = CjmlClas(inference_model_dir='../clas_infer_18')
    data_cleaner = DataClean(clas)
    clean_list = [1000, 1090, 1180, 1270, 2000, 3000, 4000, 4045, 4090
                  , 4135, 4180, 4225, 4270, 4315, 5000, 5090, 5180, 5270]
    for num in clean_list:
        data_cleaner.clean_clas(r'D:\wjs\clas_data_set\eval_data' + '\\' + str(num), num)


if __name__ == '__main__':
    # clas = CjmlClas()
    # data_clean = DataClean(clas)
    # data_clean.auto_clas(r'D:\scan_vin_imgs')
    clean()

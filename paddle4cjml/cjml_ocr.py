from paddleocr import PaddleOCR

from cjml_utils.file_util import get_image_file_list
from cjml_utils.label_util import *


class CjmlOcr:
    def __init__(self, args, use_gpu=True, use_angle_cls=True):
        """
        初始化一个推理ocr模型
        :param args: 包含模型文件路径等基本参数
        :param use_gpu: 是否使用gpu
        :param use_angle_cls: 是否使用角度分类
        """
        self.det_model_dir = args['det_model_dir']
        self.rec_model_dir = args['rec_model_dir']
        self.cls_model_dir = args['cls_model_dir']
        self.rec_char_dict_path = args['rec_char_dict_path']
        self.use_gpu = use_gpu
        self.use_angle_cls = use_angle_cls
        self.ocr_model = PaddleOCR(det_model_dir=self.det_model_dir, rec_model_dir=self.rec_model_dir,
                                   rec_char_dict_path=self.rec_char_dict_path, cls_model_dir=self.cls_model_dir,
                                   use_angle_cls=self.use_angle_cls, use_gpu=self.use_gpu, ocr_version='PP-OCRv2')

    def ocr(self, image_dir, use_decode=True, use_location=False, det=True, cls=True, rec=True):
        """
        识别图片
        :param use_location: 是否需要坐标信息 , 必须配合 use_decode=False 使用
        :param det: 是否使用det
        :param rec: 是否使用rec
        :param cls: 是否使用cls
        :param image_dir: 待识别的图片目录或单个图片路径
        :param use_decode: 是否将识别结果过滤，只保留文字信息部分
        :return: 识别结果的字典，key为图片文件名，value为识别结果list
        """
        result = {}
        image_list = get_image_file_list(image_dir)

        for image_path in image_list:
            res = self.ocr_model.ocr(image_path, det=det, rec=rec, cls=cls)
            if rec and use_decode:
                res = decode(res)
                print(res)
            elif rec and not use_location:
                res = [line[1][0] for line in res]
            image_name = image_path[image_path.rfind('\\') + 1:]
            result[image_name] = res
        return result


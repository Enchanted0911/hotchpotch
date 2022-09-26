from paddle4cjml.cjml_ocr import *

det_model_dir = 'ocr_infer/det'
rec_model_dir = 'ocr_infer/rec'
cls_model_dir = 'ocr_infer/cls'

rec_char_dict_path = 'dict/ppocr_keys_v1.txt'


def cjml_demo(image_dir):
    model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
                  , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
    ocr = CjmlOcr(model_args)
    res = ocr.ocr(image_dir, use_decode=False, use_location=True)
    print(res)


if __name__ == '__main__':
    cjml_dir = "temp_cjml_demo"
    cjml_demo(cjml_dir)




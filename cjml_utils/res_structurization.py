import cv2

from file_process import *
from cjml_utils.label_util import separate_eng_ch, separate_ch_eng_single, is_vin_then_get_vin, join_ch_and_eng

det_model_dir = '../infer_first_1k_it6/det'
rec_model_dir = '../infer_first_1k_it6/rec'
cls_model_dir = '../infer_first_1k_it6/cls'

rec_char_dict_path = '../dict/ppocr_keys_v1.txt'


def get_res_by_ocr(image_dir):
    # model_args = {'det_model_dir': det_model_dir, 'rec_model_dir': rec_model_dir
    #               , 'cls_model_dir': cls_model_dir, 'rec_char_dict_path': rec_char_dict_path}
    # ocr = CjmlOcr(model_args)
    # struct_res = ocr.ocr(image_dir, use_decode=False)
    # struct_res_str = json.dumps(struct_res)
    # with open("eval_struct/struct_res.txt", "w") as f:
    #     f.write(struct_res_str)

    return txt_dict2dict('eval_struct/struct_res.txt')


def structurization_res(res, image_dir):
    for k, v in res.items():
        vin = ''
        model = ''
        engine_model = ''
        brand = ''
        displacement = ''
        date = ''
        made_in = ''
        max_engine_power = ''
        full_str = join_ch_and_eng(v)
        processed_str = separate_eng_ch(full_str)
        eng_list = []
        for p in processed_str:
            ch, eng = separate_ch_eng_single(p)
            if model == '' and '型号' in ch and '机' not in ch:
                model = eng
                continue
            if engine_model == '' and '机型' in ch:
                if 'L' in eng and eng.count('L') > 1:
                    engine_model = eng[: eng.find('L') + 3]
                else:
                    engine_model = eng
                continue
            if vin == '' and is_vin_then_get_vin(eng) != '':
                vin = is_vin_then_get_vin(eng)
                continue
            if displacement == '' and '排量' in ch:
                displacement = eng
                continue
            if 'made' not in eng.lower() and 'power' not in eng.lower() \
                    and 'model' not in eng.lower() and 'gvw' not in eng.lower() \
                    and 'no' not in eng.lower() and 'type' not in eng.lower() and 'vin' not in eng.lower() \
                    and 'disp' not in eng.lower() and 'mfd' not in eng.lower() and 'code' not in eng.lower() \
                    and 'cap' not in eng.lower() and 'brand' not in eng.lower() and 'date' not in eng.lower() \
                    and 'kw' not in eng.lower() and 'kg' not in eng.lower() and 'ml' not in eng.lower() and '年' not in eng \
                    and '月' not in eng and '日' not in eng and '号' not in ch and 'ltd' not in eng.lower() \
                    and 'color' not in eng.lower() and 'mobile' not in eng.lower():
                eng_list.append(eng)
        eng_list.sort(key=lambda i: len(i), reverse=True)
        if model == '' and len(eng_list) > 0:
            model = eng_list[0]
        if engine_model == '' and len(eng_list) > 1:
            engine_model = eng_list[1]
        struct_list = ['vin: ' + vin, '整车型号: ' + model, '发动机型号: ' + engine_model, '发动机排量: ' + displacement]
        one_pic = Image.open(
            image_dir + '/' + k)
        blank_img = generate_blank_image(one_pic.size)
        two_pic = mark_on_pic_for_struct(struct_list, blank_img)
        pic = merge_two_pic(one_pic, two_pic)
        cv2.imwrite('struct_visual_res/' + k, pic)


if __name__ == '__main__':
    # res = fetch_label_text_content('eval_e1_it6/res_second_all.txt')
    # map(lambda x: print(x), res)
    image_dir = 'eval_e1_it6/all_det_des'
    raw_res = get_res_by_ocr(image_dir)
    structurization_res(raw_res, image_dir)

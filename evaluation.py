from cjml_utils.label_util import *
from scipy import stats
import numpy as np

def eval_pair(pair):
    """
    评估识别结果的precision recall 和 hmean

    :param pair: 包含预测值和实际值
    :return: 识别结果的三个精度指标
    """
    cnt = 0
    for c in pair[0]:
        if c.lower() in pair[1].lower():
            cnt += 1
            pair[1] = pair[1].lower().replace(c.lower(), '@', 1)
    recall = cnt / len(pair[0])
    precision = cnt / len(pair[1])
    hmean = stats.hmean([precision, recall]) if precision * recall != 0 else 0
    return [precision, recall, hmean]


def eval_pair_strict(pair):
    """
    严格判定识别是否正确，只有当识别结果完全一致时才认为识别正确

    :param pair: 包含预测值和真实值
    :return: 正确为 True
    """
    return pair[0].lower() in pair[1].lower()


def eval_pair_list(pair_list):
    """
    评估对组列表的精度指标

    :param pair_list: 待评估对组列表
    :return: 平均的 precision, recall, hmean
    """
    res = np.array([eval_pair(pair) for pair in pair_list]) if len(pair_list) > 0 else np.zeros((1, 3))
    return np.mean(res, axis=0)


def eval_pair_list_ultra_strict(pair_list):
    """
    超严格判定识别结果，只要一张图片内有一个没识别正确，则认为这张图片识别错误

    :param pair_list: 包含一张图片的预测值和真实值
    :return: 正确为1 错误为0
    """
    for p in pair_list:
        if not eval_pair_strict(p):
            return np.array([0, 0, 0])
    return np.array([1, 1, 1])


def eval_pair_list_strict(pair_list, pic_name):
    """
    严格评估对组列表的精度指标

    :param pic_name: 评估的图片名称
    :param pair_list: 待评估对组列表
    :return: 平均的 precision, recall, hmean
    """
    cnt = 0
    # wb = openpyxl.load_workbook("eval_second/error.xlsx")
    # sheet = wb['Sheet1']
    for p in pair_list:
        if eval_pair_strict(p):
            cnt += 1
    #     else:
    #         sheet.append([pic_name, p[0], p[1]])
    # wb.save("eval_second/error.xlsx")
    res = [cnt / len(pair_list), cnt / len(pair_list), cnt / len(pair_list)]
    return np.array(res)


def eval_ocr(predict, real):
    """
    评估ocr模型精度

    :param predict: 模型预测值
    :param real: 实际值
    :return: 平均的 precision, recall, hmean
    """

    # temp update
    # temp_list = [i[i.rfind('\\') + 1:] for i in get_image_file_list('only_nameplate')]

    # for ultra strict eval
    cnt = 0
    ultra_right_list = []

    all_eval = []
    for key in real:

        # temp update
        # if key not in temp_list:
        #     continue

        predict_val = predict[key]
        real_val = real[key]
        pair_list = connect(predict_val, real_val)

        # res = eval_pair_list(pair_list)
        res = eval_pair_list_strict(pair_list, key)

        all_eval.append(res)

        # for ultra strict eval
        if res[1] == 1:
            cnt += 1
            ultra_right_list.append(key)

    all_eval = np.array(all_eval)

    # for ultra strict eval
    print(cnt / len(real.keys()))

    return np.mean(all_eval, axis=0), ultra_right_list

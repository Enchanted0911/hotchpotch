import math

import numpy as np


def is_vertical_and_gain_longest_box(box_list):
    """
    判断这个box_list中的检测框是否是近似竖直的，并且返回长度最长的那个检测框
    :param box_list: 待处理的检测框集合
    :return: 检测框是否垂直，最长的检测框
    """
    max_x = 0
    max_y = 0
    res_x = []
    res_y = []
    all_x = 0
    all_y = 0
    for four_box in box_list:
        x_length = np.mean([math.dist(four_box[0], four_box[1]), math.dist(four_box[2], four_box[3])])
        y_length = np.mean([math.dist(four_box[0], four_box[3]), math.dist(four_box[1], four_box[2])])
        all_x += x_length
        all_y += y_length
        if x_length > max_x:
            max_x = x_length
            res_x = four_box
        if y_length > max_y:
            max_y = y_length
            res_y = four_box

    return all_y > all_x, res_y, res_x


def gain_all_area(box_list):
    """
    获取所有检测框的检测面积
    :param box_list: 所有检测框集合
    :return:
    """
    all_x = 0
    for four_box in box_list:
        x_length = np.mean([math.dist(four_box[0], four_box[1]), math.dist(four_box[2], four_box[3])])
        y_length = np.mean([math.dist(four_box[0], four_box[3]), math.dist(four_box[1], four_box[2])])
        all_x += x_length * y_length
    return all_x


def gain_slope(four_box):
    """
    获取检测框的斜率
    :param four_box: 单个检测框
    :return: 该检测框斜率
    """
    slope_one = (four_box[1][1] - four_box[0][1]) / (four_box[1][0] - four_box[0][0])
    slope_two = (four_box[2][1] - four_box[3][1]) / (four_box[2][0] - four_box[3][0])
    slope = (slope_one + slope_two) / 2
    return slope


def gain_slope_vertical(four_box):
    """
    获取垂直检测框斜率
    :param four_box: 单个检测框
    :return: 该检测框垂直斜率
    """
    slope_one = (four_box[2][1] - four_box[1][1]) / (four_box[2][0] - four_box[1][0] + 0.000001)
    slope_two = (four_box[3][1] - four_box[0][1]) / (four_box[3][0] - four_box[0][0] + 0.000001)
    slope = (slope_one + slope_two) / 2
    return slope


def gain_angle_by_slope(slope):
    """
    根据斜率获取角度
    :param slope: 斜率
    :return: 该斜率对应角度
    """
    return math.atan(slope) * 180 / math.pi


def gain_angle_by_add_det(box_list):
    """
    根据检测框集合获取旋转角度
    :param box_list: 检测框集合
    :return: 是否垂直检测框，旋转角度
    """
    flag, longest_y, longest_x = is_vertical_and_gain_longest_box(box_list)
    if len(longest_y) == 0:
        return False, 0
    slope = gain_slope_vertical(longest_y) if flag else gain_slope(longest_x)
    return flag, gain_angle_by_slope(slope)


def gain_lr_bound(box_list):
    left_bound = box_list[0][0][0]
    right_bound = box_list[0][1][0]
    for four_box in box_list:
        left_1 = four_box[0][0]
        right_1 = four_box[1][0]
        right_2 = four_box[2][0]
        left_2 = four_box[3][0]
        if left_bound > min(left_2, left_1):
            left_bound = min(left_2, left_1)
        if right_bound < max(right_2, right_1):
            right_bound = max(right_2, right_1)

    return left_bound, right_bound

import re


def gain_best_from_alpha_vins(alpha_vins):
    res_list_1 = []
    res_list_2 = []
    for vin in alpha_vins:
        vin_pattern_res = re.search("(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Z]{17}", vin)
        if vin_pattern_res is not None:
            if vin[0] == 'L':
                return vin
            res_list_1.append(vin_pattern_res.group())
        elif vin[0] == 'L':
            res_list_2.append(vin)
    if len(res_list_1) > 0:
        return res_list_1[0]
    return res_list_2[0]


def gain_best_from_beta_vins(beta_vins):
    vin_str_list = ["VIN", "V1N", "VTN"]
    res_list_1 = []
    res_list_2 = []
    res_list_3 = []
    res_list_4 = []
    res_list_5 = []
    res_list_ch = []
    LJ_list = []
    for vin in beta_vins:
        if len(vin) == 20 and vin[:3].upper() in vin_str_list:
            return vin[3:]
        vin_pattern_res = re.search("(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Z]{16, 20}", vin)
        if vin_pattern_res is not None:
            if len(vin) != 16 and len(vin) - vin.find("L") == 17:
                return vin[vin.find("L"):]
            elif len(vin) == 16 and vin[0] == 'L':
                res_list_1.append(vin + '1')
            elif len(vin) == 16 and vin[0] != 'L' and vin[0] != 'U':
                res_list_2.append('L' + vin)
            elif len(vin) == 16 and vin[0] == 'U':
                LJ_list.append('LJ' + vin[1:])
            elif len(vin) == 19:
                res_list_3.append(vin[1: -1])
            elif vin[0] == 'L':
                res_list_ch.append(vin[:17])
        else:
            if len(vin) != 16 and len(vin) - vin.find("L") == 17:
                res_list_4.append(vin[vin.find("L"):])
            elif len(vin) != 16 and len(vin) - vin.find("l") == 17:
                res_list_4.append(vin[vin.find("l"):])
            elif len(vin) == 16 and (vin[0] == 'L' or vin[0] == 'l'):
                res_list_5.append(vin + '1')
            elif len(vin) == 16 and (vin[0] == 'U' or vin[0] == 'u'):
                LJ_list.append('LJ' + vin[1:])
            elif len(vin) == 16 and (vin[0] != 'L' or vin[0] != 'l') and (vin[0] != 'U' and vin[0] != 'u'):
                res_list_5.append('L' + vin)
            elif len(vin) == 19:
                res_list_5.append(vin[1: -1])

    if len(res_list_1) > 0:
        return res_list_1[0]
    if len(res_list_2) > 0:
        return res_list_2[0]
    if len(res_list_ch) > 0:
        return res_list_ch[0]
    if len(res_list_3) > 0:
        return res_list_3[0]
    if len(res_list_4) > 0:
        return res_list_4[0]
    if len(res_list_5) > 0:
        return res_list_5[0]
    if len(LJ_list) > 0:
        return LJ_list[0]
    return ""


def keep_num_char(raw_list):
    """
    只留下字符串中的英文和数字

    :param raw_list: 待处理字符串列表
    :return: 不包含只有特殊字符的字符串的列表
    """
    res = [re.sub(u"([^\u0030-\u0039\u0041-\u005a\u0061-\u007a])", '', s) for s in raw_list]
    return [s for s in res if len(s) != 0]


def remove_hyphen(raw_list):
    """
    只留下字符串中的英文和数字

    :param raw_list: 待处理字符串列表
    :return: 不包含只有特殊字符的字符串的列表
    """
    res = [re.sub("-", '', s) for s in raw_list]
    return [s for s in res if len(s) != 0]


def alpha_type(res_list):
    alpha_vins = []
    beta_vins = []
    for s in res_list:
        vin = re.search("(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{16,20}", s)
        if vin is not None and len(vin.group()) == 17:
            alpha_vins.append(vin.group())
        elif vin is not None:
            beta_vins.append(vin.group())

    res = {"res": ""}
    if len(alpha_vins) == 1:
        res = {"res": alpha_vins[0]}
    elif len(alpha_vins) > 0:
        res = {"res": gain_best_from_alpha_vins(alpha_vins)}
    elif len(beta_vins) > 0:
        res = {"res": gain_best_from_beta_vins(beta_vins)}

    if res["res"] == "":
        filter_res_list = remove_hyphen(res_list)
        for fs in filter_res_list:
            vin = re.search("(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z]{17}", fs)
            if vin is not None:
                res["res"] = vin.group()

    res["res"] = res["res"].replace('I', '1').replace('O', '0')
    return res


if __name__ == '__main__':
    r_list = ['SALCA2BG9FH517784', '动机号码', 'gineNo', '070814101437204P1', '零证日期', '980', '10', 'AAA', '动机', '640']
    ress = alpha_type(r_list)
    print(ress)

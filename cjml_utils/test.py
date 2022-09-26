import cv2
import numpy as np


def gamma(source, out):
    img = cv2.imread(source, cv2.IMREAD_GRAYSCALE)
    # 归1
    Cimg = img / 255
    # 伽玛变换
    gamma = 0.7
    O = np.power(Cimg, gamma)
    O = O * 255
    # 效果
    cv2.imwrite(out, O, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])


def hist(source):
    img = cv2.imread(source, cv2.IMREAD_GRAYSCALE)
    # 求出img 的最大最小值
    Maximg = np.max(img)
    Minimg = np.min(img)
    # 输出最小灰度级和最大灰度级
    Omin, Omax = 0, 255
    # 求 a, b
    a = float(Omax - Omin) / (Maximg - Minimg)
    b = Omin - a * Minimg
    # 线性变换
    O = a * img + b
    O = O.astype(np.uint8)

    return O


def hist_auto(source):
    img = cv2.imread(source, 0)
    img = cv2.resize(img, None, fx=0.5, fy=0.5)
    # 创建CLAHE对象
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # 限制对比度的自适应阈值均衡化
    dst = clahe.apply(img)
    # 使用全局直方图均衡化
    equa = cv2.equalizeHist(img)
    # 分别显示原图，CLAHE，HE
    # cv.imshow("img", img)
    # cv2.imshow("dst", dst)
    cv2.imwrite('hist_auto.png', dst, [int(cv2.IMWRITE_PNG_COMPRESSION), 0])


def calcGrayHist(I):
    # 计算灰度直方图
    h, w = I.shape[:2]
    grayHist = np.zeros([256], np.uint64)
    for i in range(h):
        for j in range(w):
            grayHist[I[i][j]] += 1
    return grayHist


def equalHist(img):
    import math
    # 灰度图像矩阵的高、宽
    h, w = img.shape
    # 第一步：计算灰度直方图
    grayHist = calcGrayHist(img)
    # 第二步：计算累加灰度直方图
    zeroCumuMoment = np.zeros([256], np.uint32)
    for p in range(256):
        if p == 0:
            zeroCumuMoment[p] = grayHist[0]
        else:
            zeroCumuMoment[p] = zeroCumuMoment[p - 1] + grayHist[p]
    # 第三步：根据累加灰度直方图得到输入灰度级和输出灰度级之间的映射关系
    outPut_q = np.zeros([256], np.uint8)
    cofficient = 256.0 / (h * w)
    for p in range(256):
        q = cofficient * float(zeroCumuMoment[p]) - 1
        if q >= 0:
            outPut_q[p] = math.floor(q)
        else:
            outPut_q[p] = 0
    # 第四步：得到直方图均衡化后的图像
    equalHistImage = np.zeros(img.shape, np.uint8)
    for i in range(h):
        for j in range(w):
            equalHistImage[i][j] = outPut_q[img[i][j]]
    return equalHistImage


def linear(source):
    img = cv2.imread(source, 0)
    # 使用自己写的函数实现
    equa = equalHist(img)
    return equa


if __name__ == '__main__':
    source = r"D:\workspace\paddleocr\temp_err\0826.jpg"
    im = cv2.imread(source)
    print(im.shape)
    print(im[0][0][0])
    print(im[0])
    print(im[0][0])
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    print(hsv.shape)
    # print(hsv[0][0][0])
    # print(hsv[0])
    # print(hsv[0][0])
    # h, w, _ = im.shape
    # ratio = 900 / w
    # new_h = int(h * ratio)
    # new_im = cv2.resize(im, (900, new_h), interpolation=cv2.INTER_CUBIC)
    # cv2.imwrite("test.jpg", new_im)

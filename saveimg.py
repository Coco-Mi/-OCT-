import shutil
import cv2
import pydicom
import matplotlib.pyplot as plt
import numpy as np
# import pandas as pd
from numpy import zeros
from PIL import Image
import os

# plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
# # 为了坐标轴负号正常显示。matplotlib默认不支持中文，设置中文字体后，负号会显示异常。需要手动将坐标轴负号设为False才能正常显示负号。
# plt.rcParams['axes.unicode_minus'] = False

# 图片参数
h, w = 1024, 1024
cx, cy = 512, 512
maxR = 512


# 极坐标变换函数
def Polar(img):
    # 转为极坐标
    imgPolar = cv2.linearPolar(img, (cx, cy), maxR, cv2.WARP_FILL_OUTLIERS)
    # 旋转九十度
    imgPR = cv2.rotate(imgPolar, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return imgPR


# 结合两种分割方法
def combine_two_ways(th2, th20):
    threshold = 20  # 定义阈值
    img1 = th2.copy()
    img2 = th20.copy()
    height1, width1 = img1.shape
    for col in range(width1):
        if len(img1[:, col][img1[:, col] != 0]) < threshold:
            img1[:, col] = img2[:, col]
    return img1


# 图像下边界提取函数
def find_max_row(arr, m):
    arr = np.array(arr)
    max_rows = np.argmax(np.where(arr == m, np.arange(arr.shape[0])[:, None], -1), axis=0)
    return max_rows


# 下边界填充缺失值
def fill_zeros(arr):
    # 找到非零值的索引
    non_zero_idx = np.where(arr != 0)[0]
    # 找到每个零值最近的非零值的索引
    closest_non_zero_idx = np.argmin(np.abs(np.subtract.outer(np.where(arr == 0)[0], non_zero_idx)), axis=1)
    # 将所有零值替换为最近的非零值
    arr[arr == 0] = arr[non_zero_idx][closest_non_zero_idx]
    return arr


# 首尾取最小值
def min_first_last(arr):
    # 找到第一个非零值的索引
    first_nonzero_index = np.nonzero(arr)[0][0]
    # 找到最后一个非零值的索引
    last_nonzero_index = len(arr) - np.nonzero(arr[::-1])[0][0] - 1
    # 提取第一个非零值和最后一个非零值
    first_nonzero_value = arr[first_nonzero_index]
    last_nonzero_value = arr[last_nonzero_index]
    min_value = min(first_nonzero_value, last_nonzero_value)
    arr[0] = min_value  # 最大值赋给第一个值
    arr[-1] = min_value  # 最大值赋给最后一个值
    return arr


# 用线性插值填充缺失值，调用了首尾取最小值的函数
def linear_interp(arr):
    arr = min_first_last(arr)
    interp_arr = arr.copy()
    mask = arr == 0
    if np.all(~mask):
        return interp_arr
    xp = np.where(~mask)[0]
    fp = arr[~mask]
    interp_arr[mask] = np.interp(np.where(mask)[0], xp, fp)
    interp_arr = interp_arr.astype(np.int_)  # 这里要写int_,int的写法在新的np版本里弃用
    return interp_arr


# 把提取出的下边界展示出来
def array_to_image(arr):
    # 创建一个空画布
    img0 = np.zeros((1024, 1024), dtype=np.uint8)
    # 数组中每一个索引的值转化为纵坐标，并将其灰度值设为255。即一维升二维
    img0[np.arange(1024), arr] = 255
    return img0.T


# 将线下方的像素点的灰度值都设置为255，用于展示
def fill_below_line(img):
    # 找到所有灰度值为255的像素点的行列索引
    rows, cols = np.where(img == 255)
    # 对每个像素点，将它下方的所有像素点的值设为255
    for row, col in zip(rows, cols):
        img[row + 1:, col] = 255
    return img


# 删除下半部分的较小连通区域
def del_small_area(img):
    # 获得图像中的所有连通区域
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 删除面积小于指定阈值的连通区域
    for contour in contours:
        area = cv2.contourArea(contour)
        M = cv2.moments(contour)  # 求矩
        if area <= 0:
            cv2.drawContours(img, [contour], 0, 0, -1)
        else:
            # cx = int(M['m10']/M['m00']) # 求x坐标
            every_cy = int(M['m01'] / M['m00'])  # 求y坐标
            if (area < 5000 and every_cy > 600) or (area < 8000 and every_cy > 800):
                cv2.drawContours(img, [contour], 0, 0, -1)
    return img


# 获得最大连通域的质心坐标
def max_xy(img):
    # 获得图像中的所有连通区域
    contours, hierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    areas = [cv2.contourArea(c) for c in contours]
    max_index = np.argmax(areas)
    max_contour = contours[max_index]

    # 计算最大连通区域的质心坐标
    M = cv2.moments(max_contour)
    m_cx = int(M['m10'] / M['m00'])
    m_cy = int(M['m01'] / M['m00'])
    return m_cx, m_cy


def saveimg(img):
    img2 = img.copy()
    # 画圆
    cv2.circle(img2, (cx, cy), 60, 15, -1)

    # 滤波 高斯模糊（不采用，后改为中值滤波）
    # img = cv2.GaussianBlur(img, (11, 11), 0)

    # 对原图进行固定阈值分割
    ret, th_z = cv2.threshold(img2, 20, 255, cv2.THRESH_BINARY)
    # 求最大连通区域的质心坐标
    m_cx, m_cy = max_xy(th_z)

    # 极坐标变换
    imgPR = Polar(img2)

    # 中值滤波
    imgPR = cv2.medianBlur(imgPR, 11)

    # OTSU法分割
    ret, th2 = cv2.threshold(imgPR, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 固定阈值分割（20）
    ret, th20 = cv2.threshold(imgPR, 20, 255, cv2.THRESH_BINARY)

    # 求固定阈值分割出来的最大连通域的质心
    # m_cx,m_cy = max_xy(th20)

    # 结合两种方法
    th2 = combine_two_ways(th2, th20)

    # 删除图片下半部分小连通量
    th2 = del_small_area(th2)

    # 下边界的纵坐标即为
    bottom_y = find_max_row(th2, 255)

    # y = fill_zeros(y)
    # 原来是最近邻插值，现改为线性插值
    bottom_y = linear_interp(bottom_y)

    # 计算半径（已修正）
    r_x = (len(bottom_y) - bottom_y) / 2

    # 用r计算面积
    S_x = 3.14 * sum(x ** 2 for x in r_x) / len(r_x)
    area = S_x / 10000

    return bottom_y, area, m_cx, m_cy


def run(self, filename,global_ms):
    # 读取DICOM文件
    img_file = filename
    # './CHEN XIA/20220812101214(2022-08-12 9).dcm'
    ds = pydicom.dcmread(img_file)

    pixel_array = ds.pixel_array
    pixel_array_out = pixel_array
    combine = pixel_array
    area = zeros(len(pixel_array))

    if self.ui.ifSave.isChecked():
        # 创建文件夹
        path = filename.rstrip('.dcm') + "导出图片"
        # 如果没有就创建，有就先删除再创建
        if not os.path.exists(path):
            os.mkdir(path)
        else:
            shutil.rmtree(path)
            os.mkdir(path)
        # if os.path.exists(path):
        #     shutil.rmtree("path")
        # os.makedirs(path)

    # 遍历所有图片
    # 定义一个列表来保存所有质心坐标
    centroids_list = []
    for i in range(len(pixel_array)):
        # 对第 i 张图片进行处理, 将处理后的图片存储回 pixel_array 列表中
        bottom_y, area[i], m_cx, m_cy = saveimg(pixel_array[i])
        centroids_list.append((m_cx, m_cy))
        if self.ui.ifSave.isChecked():
            boundary = array_to_image(bottom_y)
            boundary2 = fill_below_line(boundary)

            boundary90 = cv2.rotate(boundary, cv2.ROTATE_90_CLOCKWISE)
            rect_img = cv2.linearPolar(boundary90, (cx, cy), maxR, cv2.WARP_INVERSE_MAP)
            # 图像融合
            # combine[i] = cv2.addWeighted(pixel_array[i], 0.5, pixel_array_out, 0.5, 0)
            add = np.concatenate((pixel_array[i], rect_img), axis=1)  # 横向拼接
            # 保存图片和拼接图片
            im_rect = Image.fromarray(rect_img)
            im_add = Image.fromarray(add)
            im_rect.save(path + "/" + str(i) + ".jpeg")
            im_add.save(path + "/对照" + str(i) + ".jpeg")

        # 进度条更新 传出信号，避免在该线程中操纵ui
        global_ms.bar_setvalue.emit(i)
        # self.ui.progressBar.setValue(i)
    # 全部运行结束
    return area, ds, centroids_list
    # pixel_array_out[1].save('./save.png')

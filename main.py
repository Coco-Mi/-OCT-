# import sys
import numpy as np
# from matplotlib import pyplot as plt

# 自定义函数所在文件
import saveimg
# from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
from PyQt5 import uic
import pyqtgraph as pg
import scipy.signal as signal
import time
from PIL import Image
import scipy.io as sio
# import pandas as pd


class Stats:

    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi('main.ui')
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        self.med_area = None
        self.peaks = None
        self.area = None

        self.filename = 0  # 默认为0 用于检测导入文件是否成功

        self.ui.analyse.clicked.connect(self.analyse)
        self.ui.selectFile.clicked.connect(self.importfile)
        # 基于管腔质心提示
        self.ui.checkBox.clicked.connect(self.by_xy)
        # 绘制图像初始背景
        self.first_graph()

        # 图像交互
        # GraphicsScene是PyQtGraph中表示场景的类。当用户与PyQtGraph中的对象进行交互时（例如，单击鼠标或移动鼠标），
        # PyQtGraph会自动生成相应的事件，并将其发送到事件处理程序。
        self.ui.graphWidget.scene().sigMouseClicked.connect(self.interaction)
        # 默认选中只查看模式
        self.ui.view.setChecked(True)
        # 设置最浅级数
        self.deep = 3
        self.ui.setBranch.setPlaceholderText('3')
        self.ui.setBranch.textChanged.connect(self.setbranch)
        # 默认显示小数位数为3
        self.around_n = 3
        self.ui.setAround.setPlaceholderText('3')
        # 这里修改了显示小数位数后，仅重新调用展示函数，也就是说不重新计算那个数组
        self.ui.setAround.textChanged.connect(self.setAround1)

        # 进度条初始化
        self.ui.progressBar.setRange(0, 269)
        self.ui.progressBar.setValue(0)

        self.ui.actionmat.triggered.connect(self.outputmat)
        self.ui.actionnumpy.triggered.connect(self.outputnumpy)
        self.ui.actiontxt.triggered.connect(self.outputtxt)

        self.ui.actionmat_2.triggered.connect(self.outputmat_2)
        self.ui.actionnumpy_2.triggered.connect(self.outputnumpy_2)
        self.ui.actiontxt_2.triggered.connect(self.outputtxt_2)

        self.ui.actionmat_3.triggered.connect(self.outputmat_3)
        self.ui.actionnumpy_3.triggered.connect(self.outputnumpy_3)
        self.ui.actiontxt_3.triggered.connect(self.outputtxt_3)

    # 导出1 原始数据
    # 导出面积 mat格式
    def outputmat(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'mat(*.mat)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        sio.savemat(filepath, {'area_data': self.area})

    # 导出面积 txt格式
    def outputtxt(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'txt(*.txt)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.savetxt(filepath, self.area)

    # 导出面积 numpy格式
    def outputnumpy(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'numpy(*.npy)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.save(filepath, self.area)

    # 导出2 各级平均面积
    # 导出面积 mat格式
    def outputmat_2(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'mat(*.mat)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        sio.savemat(filepath, {'area_data': self.mean_branch})

    # 导出面积 txt格式
    def outputtxt_2(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'txt(*.txt)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.savetxt(filepath, self.mean_branch)

    # 导出各级平均面积 numpy格式
    def outputnumpy_2(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'numpy(*.npy)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.save(filepath, self.mean_branch)

    # 导出3 各级面积中位数
    # 导出面积 mat格式
    def outputmat_3(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'mat(*.mat)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        sio.savemat(filepath, {'area_data': self.median_branch})

    # 导出面积 txt格式
    def outputtxt_3(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'txt(*.txt)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.savetxt(filepath, self.median_branch)

    # 导出面积 numpy格式
    def outputnumpy_3(self):
        filepath, type = QFileDialog.getSaveFileName(None, "文件保存", "/",
                                                     'numpy(*.npy)')
        print(filepath)
        # 前面是地址，后面是文件类型,得到输入地址的文件名和地址txt(*.txt*.xls);;image(*.png)不同类别
        np.save(filepath, self.median_branch)

    # 显示图片
    def imgShow(self, i):
        lbl = self.ui.imgShow
        pixel_array = self.ds.pixel_array
        img_pil = Image.fromarray(pixel_array[i])
        img_pix = img_pil.toqpixmap()  # QPixmap
        # img_img = img_pil.toqimage()  # QImage
        # img = QPixmap(pixel_array[i])
        lbl.setPixmap(img_pix)  # 在label上显示图片
        # lbl.setScaledContents(True)  # 让图片自适应label大小
        # 宽高等比例自适应大小
        lbl.setPixmap(img_pix.scaledToWidth(lbl.width()))
        lbl.setPixmap(img_pix.scaledToHeight(lbl.height()))
        # hbox.addWidget(lbl)
        lbl.setWindowTitle('OCT影像')
        lbl.show()

    # 图像交互
    def interaction(self, event):
        # 展示对应位置的图片
        pos = event.scenePos()
        x = self.ui.graphWidget.plotItem.vb.mapSceneToView(pos).x()
        y = self.ui.graphWidget.plotItem.vb.mapSceneToView(pos).y()
        print("Clicked at x=%0.2f, y=%0.2f" % (x, y))
        intx = int(x)
        self.imgShow(intx)

        if self.ui.newbranch.isChecked():
            med_y = self.med_area[intx]
            # print(type(self.area[1]))
            s = pg.ScatterPlotItem(x=[intx], y=[med_y], pen="red", brush="r", name='新增点')
            s.setSymbol("o")  # 设置散点形状为圆圈
            s.setSize(10)  # 设置散点大小为10
            self.ui.graphWidget.addItem(s)  # 添加散点到PlotWidget
            # 比第几个分叉点小就在第几个位置插入
            for i in range(len(self.peaks)):
                if intx < self.peaks[i]:
                    self.peaks = np.insert(self.peaks, i, intx)
                    print(self.peaks)
                    break
            self.mean_midean()

        if self.ui.deletebranch.isChecked():
            new_peaks = []
            for i in range(len(self.peaks)):
                if (intx - 5) <= self.peaks[i] <= (intx + 5):
                    continue  # 如果要删除该元素，就不要将其添加到新列表中
                new_peaks.append(self.peaks[i])
            if len(new_peaks) <= 1:
                msg_box = QMessageBox(QMessageBox.Critical, '错误', '分段点过少')
                msg_box.exec_()
                return
            self.peaks = np.array(new_peaks)
            # print(len(self.peaks))
            # print(self.peaks)
            self.mean_midean()
            gW1 = self.ui.graphWidget
            gW1.clear()
            gW1.plot(np.array(range(0, len(self.med_area))), self.med_area, pen=pg.mkPen(width=2), name='面积')
            gW1.plot(self.peaks, self.med_area[self.peaks], pen=None, symbol='o', name='分叉点')

    # 图像初始化 这一步是为了防止进入界面的时候图表什么都没有
    def first_graph(self):
        gW1 = self.ui.graphWidget
        gW1.setBackground('w')
        # 设置图表标题、颜色、字体大小
        gW1.setTitle("管腔面积变化图&分叉点检测", size='15pt')
        gW1.setLabel("left", "面积（mm2）")
        gW1.setLabel("bottom", "图像序号")
        # 显示表格线
        gW1.showGrid(x=True, y=True)
        gW1.addLegend(size=(150, 80))

    # 设置展示均值和中值要保留几位小数
    def setAround1(self, n):
        if n != '':
            self.around_n = int(n)
        else:
            self.around_n = 3
        self.show_mean_median()

    # 手动设置最深分叉级数
    def setbranch(self, deep):
        if deep != '':
            self.deep = int(deep)
            self.mean_midean()

    # 计算均值和中位数
    def mean_midean(self):
        self.len_branch = len(self.peaks) + 1
        self.mean_branch = np.zeros(self.len_branch)
        self.median_branch = np.zeros(self.len_branch)
        for i in range(len(self.peaks)):
            if i == 0:
                self.mean_branch[i] = np.mean(self.med_area[:self.peaks[i]])
                self.mean_branch[i + 1] = np.mean(self.med_area[self.peaks[i]:self.peaks[i + 1]])
                self.median_branch[i] = np.median(self.med_area[:self.peaks[i]])
                self.median_branch[i + 1] = np.median(self.med_area[self.peaks[i]:self.peaks[i + 1]])
            elif i < len(self.peaks) - 1:
                self.mean_branch[i + 1] = np.mean(self.med_area[self.peaks[i]:self.peaks[i + 1]])
                self.median_branch[i + 1] = np.median(self.med_area[self.peaks[i]:self.peaks[i + 1]])
            else:
                self.mean_branch[i + 1] = np.mean(self.med_area[self.peaks[i]:])
                self.median_branch[i + 1] = np.median(self.med_area[self.peaks[i]:])
        print(self.mean_branch, self.median_branch)
        self.show_mean_median()

    # 展示均值和中位数
    def show_mean_median(self):
        # 展示时保留n位小数
        show_mean_branch = np.around(self.mean_branch, self.around_n)
        show_median_branch = np.around(self.median_branch, self.around_n)
        table = self.ui.tableWidget
        table.setColumnCount(self.len_branch)
        deep = []
        # 若非空
        if self.deep:
            for i in range(self.len_branch):
                deep.append(str(self.deep + self.len_branch - i - 1))
            table.setHorizontalHeaderLabels(deep)
            print("设置")

        for i in range(self.len_branch):
            # deep = QTableWidgetItem(str(self.deep-i))
            # table.setItem(0, i, deep)
            item_mean = QTableWidgetItem(str(show_mean_branch[i]))
            table.setItem(0, i, item_mean)
            item_median = QTableWidgetItem(str(show_median_branch[i]))
            table.setItem(1, i, item_median)

    # 绘制中位数
    # def plot_median(self):
    #    gW1 = self.ui.graphWidget
    #    gW1.plot(x, self.med_area, pen=pg.mkPen(width=2), name='面积')

    # 导入文件
    def importfile(self):
        # 其中self指向自身，"读取文件夹"为标题名，"./"为打开时候的当前路径
        self.filename, _ = QFileDialog.getOpenFileName(self.ui, "导入文件", "./CHEN XIA/", "Files(*.dcm)")  # 起始路径
        if self.filename:
            self.ui.fileName.setText(self.filename)
            print(f"file:{self.filename}")
        else:
            QMessageBox.critical(self.ui, "出错", "导入失败")

    # 分析
    def analyse(self):
        if self.filename:
            T1 = time.time()
            self.area, self.ds, self.centroids_list = saveimg.run(self, self.filename)
            T2 = time.time()
            t = int(T2 - T1)
            self.ui.runtime.setText('耗时%s秒' % t)
            print(self.filename)
            self.show_area()
            self.findBranch(self.area)
            self.show_information()
            self.mean_midean()
            print(self.centroids_list)
        else:
            QMessageBox.critical(self.ui, "出错", "没有导入文件")

    # 显示患者信息和图像信息
    def show_information(self):
        ID = self.ds.PatientID
        time = self.ds.ContentTime
        manu = self.ds.Manufacturer
        frame = str(self.ds.NumberOfFrames)
        # 原编码格式为iso8859，使用gb18030解码
        encode = self.ds.PatientName.encodings  # 为了通用性，这里先查看编码格式是多少
        name = str(self.ds.PatientName.encode(encode), 'gb18030')
        self.ui.ID.setText(ID)
        self.ui.name.setText(name)
        self.ui.time.setText(time)
        self.ui.manu.setText(manu)
        self.ui.frame.setText(frame)

    # 保存面积数组
    def show_area(self):
        np.save(self.filename.rstrip('.dcm') + "导出数组.npy", self.area)
        print(self.area)
        x = np.array(range(0, len(self.area)))

    # 分叉点检测并绘制图像和分叉点图像
    def findBranch(self, arr):
        self.x = np.array(range(0, len(arr)))

        # 一维中值滤波
        self.med_area = signal.medfilt(arr, 9)

        # 求梯度
        gra_area = np.gradient(self.med_area)

        # 峰值检测
        self.peaks, _ = signal.find_peaks(gra_area, height=0.2, distance=25)
        self.peaks = self.peaks[np.sort(np.argsort(self.peaks)[-5:])]
        print(self.peaks)
        # self.peaks = sorted(peaks, key=lambda x: -gra_area[x])[:5]
        self.plot_basic()

    def plot_basic(self):
        # 画图
        gW1 = self.ui.graphWidget
        # 前面初始图已经将背景标题什么的都设置好了，这里只要画线和图例就行
        # 创建 PlotDataItem ，缺省是曲线图
        # curve = gW2.plot(pen=pg.mkPen('b'))  # 线条颜色
        gW1.setLimits(xMin=0, yMin=0, xMax=len(self.med_area), yMax=np.max(self.med_area) + 1)
        # 先清除之前画的东西（针对用户按了多次分析的情况）
        gW1.clear()
        gW1.plot(self.x, self.med_area, pen=pg.mkPen(width=2), name='面积')
        gW1.plot(self.peaks, self.med_area[self.peaks], pen=None, symbol='o', name='分叉点')
        # gW1.addLegend(size=(150, 80))
        # 设置十字光标

    def by_xy(self):
        if self.ui.checkBox.isChecked():
            print("yes")
            # 计算每两个相邻图像的质心坐标之间的距离
            centroids = np.array(self.centroids_list)
            distances = np.linalg.norm(centroids[1:] - centroids[:-1], axis=1)
            # 峰值检测
            peaks, _ = signal.find_peaks(distances, height=1, distance=20)
            peaks = sorted(peaks, key=lambda x: -distances[x])[:5]
            print(peaks)

            # 画图
            gW1 = self.ui.graphWidget
            gW1.plot(peaks, self.med_area[peaks], pen=None, symbol='t',symbolBrush=(0, 255, 0), label="基于管腔质心变化得到的分叉点")
            gW1.addLegend(size=(150, 80))
        else:
            print("no")
            # 画图
            gW1 = self.ui.graphWidget
            # 前面初始图已经将背景标题什么的都设置好了，这里只要画线和图例就行
            # 创建 PlotDataItem ，缺省是曲线图
            # curve = gW2.plot(pen=pg.mkPen('b'))  # 线条颜色
            gW1.setLimits(xMin=0, yMin=0, xMax=len(self.med_area), yMax=np.max(self.med_area) + 1)
            # 先清除之前画的东西（针对用户按了多次分析的情况）
            gW1.clear()
            gW1.plot(self.x, self.med_area, pen=pg.mkPen(width=2), name='面积')
            gW1.plot(self.peaks, self.med_area[self.peaks], pen=None, symbol='o', name='分叉点')


    def output(self):
        self.mean_branch.to_excel(self.path + "/" + "平均管径.xls", index=False)


app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()

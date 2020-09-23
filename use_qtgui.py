#!/usr/bin/python3
# -*- coding: utf-8 -*-
 
"""
Py40.com PyQt5 tutorial 
 
In this example, we create a simple
window in PyQt5.
 
author: Jan Bodnar
website: py40.com 
last edited: January 2015
"""
 
import sys
 
#这里我们提供必要的引用。基本控件位于pyqt5.qtwidgets模块中。
from PyQt5.QtWidgets import (QWidget, QToolTip, QPushButton, QApplication)
from PyQt5.QtGui import QIcon
 
 
# if __name__ == '__main__':
    # #每一pyqt5应用程序必须创建一个应用程序对象。sys.argv参数是一个列表，从命令行输入参数。
    # app = QApplication(sys.argv)
    # #QWidget部件是pyqt5所有用户界面对象的基类。他为QWidget提供默认构造函数。默认构造函数没有父类。
    # w = QWidget()
    # #resize()方法调整窗口的大小。这离是250px宽150px高
    # w.resize(500, 500)
    # #move()方法移动窗口在屏幕上的位置到x = 300，y = 300坐标。
    # w.move(300, 300)
    # #设置窗口的标题
    # w.setWindowTitle('自动诊断工具_HZCV1.0')
    # #显示在屏幕上
    # w.show()
    
    # #系统exit()方法确保应用程序干净的退出
    # #的exec_()方法有下划线。因为执行是一个Python关键词。因此，exec_()代替
    # sys.exit(app.exec_())

class MainClass(QWidget):

    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        #设置窗口的位置和大小
        self.setGeometry(300, 300, 300, 220)  
        #设置窗口的标题
        self.setWindowTitle('Icon')
        #设置窗口的图标，引用当前目录下的web.png图片
        # self.setWindowIcon(QIcon('web.png'))        
        
        #显示窗口
        self.show()

if __name__ == '__main__':
    #创建应用程序和对象
    app = QApplication(sys.argv)
    ex = MainClass()
    sys.exit(app.exec_()) 
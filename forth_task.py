import itertools
import math
from typing import List, Any
import numpy as np

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect, QLine
import sys


class ForthTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.x1 = -4
        self.x2 = 4
        self.y1 = -4
        self.y2 = 4
        self.top = []
        self.bottom = []

        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('Forth Task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))

        self.draw_function(qp)

        qp.end()

    def draw_function(self, qp: QPainter):
        for i in range(self.geometry().width()):
            self.top.append(self.geometry().height())
            self.bottom.append(0)
        n = 50
        m = self.geometry().width() * 2

        mx = self.geometry().width()
        my = self.geometry().height()
        minx = -7
        maxx = -minx
        miny = minx
        maxy = maxx

        for i in range(n):
            x = self.x2 + i * (self.x1 - self.x2) / n
            for j in range(m):
                y = self.y2+j * (self.y1-self.y2) / m
                z = self.function(x, y)
                xx, yy = self.isometric_projection(x, y, z)
                xx = round((xx - minx) * mx / (maxx - minx))
                yy = round((yy - miny) * my / (maxy - miny))
                if (yy > self.bottom[xx]):
                    qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.bottom[xx]=yy
                if (yy < self.top[xx]):
                    qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.top[xx]=yy
        self.top =[]
        self.bottom =[]
        for i in range(self.geometry().width()):
            self.top.append(self.geometry().height())
            self.bottom.append(0)

        for i in range(n):
            y = self.y2 + i * (self.y1 - self.y2) / n
            for j in range(m):
                x = self.x2+j * (self.x1-self.x2) / m
                z = self.function(x, y)
                xx, yy = self.isometric_projection(x, y, z)
                xx = round((xx - minx) * mx / (maxx - minx))
                yy = round((yy - miny) * my / (maxy - miny))
                if (yy > self.bottom[xx]):
                    qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.bottom[xx]=yy
                if (yy < self.top[xx]):
                    qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
                    qp.drawPoint(xx, yy)
                    self.top[xx]=yy

    def function(self, x, y):
        return math.cos(x*y)

    def isometric_projection(self, x,y,z):
        return (y-x)*math.sqrt(3.0)/2, (x+y)/2-z

def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    sys._excepthook = sys.excepthook

    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    ex = ForthTask()
    sys.exit(app.exec_())

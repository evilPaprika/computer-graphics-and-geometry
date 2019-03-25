import itertools
import math
from typing import List, Any

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


class FirstTask(QWidget):
    polygon: List[QPoint]

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.polygon_is_build = False
        self.polygon = []
        self.polygon_shards = []
        self.concave_vertices = []

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Third task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        if not self.polygon_is_build:
            if not self.polygon or not (self.polygon[0] - event.pos()).manhattanLength() < 10:
                self.polygon.append(event.pos())
                self.update()
                return
            self.polygon_is_build = True
            self.split_polygon()
            self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.paint_polygon(qp)
        if self.polygon_is_build:
            qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            for vertex in self.concave_vertices:
                qp.drawPoint(vertex)

        qp.end()

    def split_polygon(self):
        self.find_concave_vertices()

    def find_concave_vertices(self):
        # TODO добавить точки чтобы был конец
        for i in range(2, len(self.polygon)):
            if (self.polygon[i - 1].x() - self.polygon[i - 2].x()) * (self.polygon[i].y() - self.polygon[i - 1].y()) - (
                    self.polygon[i].x() - self.polygon[i - 1].x()) * (
                    self.polygon[i - 1].y() - self.polygon[i - 2].y()) < 0:
                self.concave_vertices.append(self.polygon[i - 1])

    def paint_polygon(self, qp):
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
        for vertex in self.polygon:
            qp.drawPoint(vertex)
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        for i in range(1, len(self.polygon)):
            qp.drawLine(self.polygon[i - 1], self.polygon[i])

        if self.polygon_is_build:
            qp.drawLine(self.polygon[-1], self.polygon[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstTask()
    sys.exit(app.exec_())

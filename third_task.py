import itertools
import math
from typing import List, Any

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect, QLine
import sys


class ThirdTask(QWidget):
    polygon: List[QPoint]

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.polygon_is_build = False
        self.polygon = []
        self.polygon_shards = []
        self.concave_vertices = []

        self.get_line_intersection(QPoint(10, 0), QPoint(10, 1), QPoint(5, 5), QPoint(15, 5))

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
            self.update()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))

        
        if self.polygon_is_build:
            self.polygon_shards = self.split_polygon(self.polygon, qp)

            for poly in self.polygon_shards:
                self.paint_polygon(qp, poly)
            qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
            for vertex in self.concave_vertices:
                qp.drawPoint(vertex)
        else:
            self.paint_polygon(qp, self.polygon)
        qp.end()

    def split_polygon(self, polygon, qp):
        concave_vertex = self.find_concave_vertex(polygon)
        if not concave_vertex:
            return [polygon]
        edges = [QLine(*(polygon + polygon)[i:i + 2]) for i in range(0, len(polygon), 1)]
        self.concave_vertices.append(concave_vertex)
        i = polygon.index(concave_vertex)

        intersection, split_edge = self.find_closest_intersection(polygon[i - 1], concave_vertex, edges)

        if not split_edge or not intersection:
            return [polygon]
        polygon_one = [intersection]
        polygon_two = [intersection, concave_vertex]
        j = 1
        while True:
            vertex_one = polygon[i - j]
            if vertex_one == split_edge.p1():
                polygon_one.append(vertex_one)
                polygon_two.insert(0, split_edge.p2())
                break
            if vertex_one == split_edge.p2():
                polygon_one.append(vertex_one)
                polygon_two.insert(0, split_edge.p1())
                break
            j += 1
            polygon_one.append(vertex_one)
        k = 1
        while True:
            vertex_two = polygon[(i + k) % len(polygon)]
            if vertex_two == split_edge.p1():
                break
            if vertex_two == split_edge.p2():
                break
            k += 1
            polygon_two.append(vertex_two)
        return self.split_polygon(polygon_one, qp) + (self.split_polygon(polygon_two, qp))

    def find_concave_vertex(self, polygon):
        if self.area_by_shoelace(polygon) < 0:
            polygon = polygon[::-1]
        for i in range(0, len(polygon)):
            if (polygon[i - 1].x() - polygon[i - 2].x()) * (polygon[i].y() - polygon[i - 1].y()) - (
                    polygon[i].x() - polygon[i - 1].x()) * (
                    polygon[i - 1].y() - polygon[i - 2].y()) < 0:
                return polygon[i - 1]

    def find_closest_intersection(self, p0: QPoint, p1: QPoint, edges):
        min_intersection, split_edge = None, None
        min_length = None
        for edge in edges:
            intersection = self.get_line_intersection(p0, p1, edge.p1(), edge.p2())
            if intersection == p0 or intersection == p1:
                continue
            if intersection and not min_intersection:
                min_intersection, split_edge = intersection, edge
                min_length = (p1 - intersection).manhattanLength()
                continue
            if intersection and (p1 - intersection).manhattanLength() < min_length:
                min_intersection, split_edge = intersection, edge
        return min_intersection, split_edge

    def get_line_intersection(self, p0: QPoint, p1: QPoint, p2: QPoint, p3: QPoint):
        # https://stackoverflow.com/a/1968345
        # алгоритм модифицирован чтобы находить пересечение с лучем образованым первой линией
        s1 = QPoint(p1.x() - p0.x(), p1.y() - p0.y())
        s2 = QPoint(p3.x() - p2.x(), p3.y() - p2.y())

        try:
            s = (-s1.y() * (p0.x() - p2.x()) + s1.x() * (p0.y() - p2.y())) / (-s2.x() * s1.y() + s1.x() * s2.y())
            t = (s2.x() * (p0.y() - p2.y()) - s2.y() * (p0.x() - p2.x())) / (-s2.x() * s1.y() + s1.x() * s2.y())

            if 0 <= s <= 1 and t > 0:
                intersection = QPoint(p0.x() + (t * s1.x()), p0.y() + (t * s1.y()))
                return intersection
        except ZeroDivisionError:
            pass

        return None

    def area_by_shoelace(self, polygon):
        area = 0
        for i in range(len(polygon)):
            area += (polygon[i - 1].x() - polygon[i].x()) * (polygon[i - 1].y() + polygon[i].y())
        return area

    def paint_polygon(self, qp, polygon):
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
        for vertex in polygon:
            qp.drawPoint(vertex)
            qp.drawText(vertex, str(vertex.x()) + ", " + str(vertex.y()))
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        for i in range(1, len(polygon)):
            qp.drawLine(polygon[i - 1], polygon[i])

        if self.polygon_is_build:
            qp.drawLine(polygon[-1], polygon[0])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ThirdTask()
    sys.exit(app.exec_())

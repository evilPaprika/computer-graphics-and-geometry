import math
import numpy as np
from itertools import combinations, chain

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect, QLine, QTimer
import sys


class FifthTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.x1 = -3
        self.x2 = 3
        self.y1 = -3
        self.y2 = 3

        self.square = np.array([[2, -2, 0, 0, 0, 0],
                                [0, 0, 2, -2, 0, 0],
                                [0, 0, 0, 0, 1, -1],
                                [1, 1, 1, 1, 1, 1], ])

        self.square2 = np.array([[1, -1, 0, 0, 0, 0],
                                 [0, 0, 1, -1, 0, 0],
                                 [0, 0, 0, 0, 2, -2],
                                 [1, 1, 1, 1, 1, 1], ])

        self.shapes = [self.square, self.square2]

        self.rotation_angle_x = 0
        self.rotation_angle_y = 0
        self.rotation_angle_z = 0
        self.rotate()

        self.init_ui()

        self._status_update_timer = QTimer(self)
        self._status_update_timer.timeout.connect(self.rotate)
        self._status_update_timer.start(50)

    def rotate(self):
        # self.rotation_angle_x += 0.05
        self.rotation_angle_y += 0.02
        # self.rotation_angle_z += 0.1
        self.transformed_shapes = map(lambda shape: self.transform(shape), self.shapes)
        self.lines_to_draw = chain(*map(lambda shape: self.find_shape_edges(shape), self.transformed_shapes))

        self.init_ui()
        self.update()

    def find_shape_edges(self, shape):
        transposed_shape = shape.transpose().tolist()
        grouped_by_two_planes = combinations(transposed_shape, 2)
        result = []
        for two_planes in grouped_by_two_planes:
            line = []
            for third_plane in transposed_shape:
                p1 = two_planes[0]
                p2 = two_planes[1]
                p3 = third_plane
                c = 0
                if np.dot(p1, [0, 0, 1, 0]) <= 0: c += 1
                if np.dot(p2, [0, 0, 1, 0]) <= 0: c += 1
                if np.dot(p3, [0, 0, 1, 0]) <= 0: c += 1
                if c == 3:
                    continue
                if p1 == p3 or p2 == p3:
                    continue
                try:
                    new_point = np.linalg.solve([p1[:3], p2[:3], p3[:3]], np.array([-p1[3], -p2[3], -p3[3]])).tolist()
                    if (-1e+15 < new_point[0] < 1e+15 and -1e+15 < new_point[1] < 1e+15 and -1e+15 < new_point[
                        2] < 1e+15):
                        line.append(new_point)
                except:
                    continue
            if len(line) == 2: result.append(line)
        return result

    def init_ui(self):
        self.setWindowTitle('Fifth Task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_shape(qp)
        qp.end()

    def draw_shape(self, qp: QPainter):
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        for line in self.lines_to_draw:
            qp.drawLine(self.plane_to_screen(line[0]), self.plane_to_screen(line[1]))

    def plane_to_screen(self, v):
        xp, yp = self.front_projection(v)
        xx = round((xp - self.x1) * self.geometry().width() / (self.x2 - self.x1))
        yy = round((yp - self.y1) * self.geometry().height() / (self.y2 - self.y1))
        return QPoint(xx, yy)

    def front_projection(self, v):
        return v[0], v[1]

    def homog_to_screen(self, v):
        vh = self.heal_homog(v)
        xp, yp = vh[0], vh[1]
        xx = round((xp - self.x1) * self.geometry().width() / (self.x2 - self.x1))
        yy = round((yp - self.y1) * self.geometry().height() / (self.y2 - self.y1))
        return QPoint(xx, yy)

    def heal_homog(self, v):
        return [v[0] / v[3], v[1] / v[3], v[2] / v[3], 1]

    def transform(self, m):
        return self.rotation_z(self.rotation_x(self.rotation_y(m)))

    def rotation_x(self, m):
        angle = self.rotation_angle_x
        rot_matrix = np.array([
            [1, 0, 0, 0],
            [0, math.cos(angle), math.sin(angle), 0],
            [0, -math.sin(angle), math.cos(angle), 0],
            [0, 0, 0, 1],
        ])

        return np.dot(np.linalg.inv(rot_matrix), m)

    def rotation_y(self, m):
        angle = self.rotation_angle_y
        rot_matrix = np.array([
            [math.cos(angle), 0, -math.sin(angle), 0],
            [0, 1, 0, 0],
            [math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1],
        ])

        return np.dot(np.linalg.inv(rot_matrix), m)

    def rotation_z(self, m):
        angle = self.rotation_angle_z
        rot_matrix = np.array([
            [math.cos(angle), math.sin(angle), 0, 0],
            [-math.sin(angle), math.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ])

        return np.dot(np.linalg.inv(rot_matrix), m)

    # def projection(self, x, y, z):
    #     return self.front_projection(x, y, z)
    #
    # def z_perspective_projection(self):
    #     # not done
    #     proj = numpy.array([[1, 0, 0, 0],
    #                  [0, 1, 0, 0],
    #                  [0, 0, 0, 0],
    #                  [1, 0, 1, 1], ])

    #
    # def isometric_projection(self, x, y, z):
    #     return (y - x) * math.sqrt(3.0) / 2, (x + y) / 2 - z
    #
    # def dimetric_projection(self, x, y, z):
    #     return -x / (2 * math.sqrt(2)) + y, x / (2 * math.sqrt(2)) - z


#
# class HomogenousVector:
#     def __init__(self, v):
#         self.x = v[0]
#         self.y = v[1]
#         self.z = v[2]
#         self.w = v[3]
#
#     def toList(self):
#         return [self.x, self.y, self.z, self.w]
#
#     def toScreen(self):
#

def my_exception_hook(exctype, value, traceback):
    print(exctype, value, traceback)
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    ex = FifthTask()
    sys.exit(app.exec_())
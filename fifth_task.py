import math
import numpy as np
from itertools import combinations, chain, permutations
from functools import reduce
from scipy.optimize import linprog


from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont, QMouseEvent
from PyQt5.QtCore import Qt, QPoint, QRect, QLine, QTimer
import sys

np.set_printoptions(precision=1)


class FifthTask(QWidget):

    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)

        self.x1 = -2.5
        self.x2 = 2.5
        self.y1 = -2.5
        self.y2 = 2.5

        square = [([2, 1, 1], [1, 3, 6]),
                  ([-1, 1, 1], [1, 2, 3]),
                  ([2, -1, 1], [3, 4, 6]),
                  ([2, 1, -1], [1, 5, 6]),
                  ([-1, -1, 1], [2, 3, 4]),
                  ([-1, 1, -1], [1, 2, 5]),
                  ([2, -1, -1], [4, 5, 6]),
                  ([-1, -1, -1], [2, 4, 5])]

        square2 = [([3, 1, 1], [1, 3, 6]),
                   ([1, 1, 1], [1, 2, 3]),
                   ([3, -1, 1], [3, 4, 6]),
                   ([3, 1, -1], [1, 5, 6]),
                   ([1, -1, 1], [2, 3, 4]),
                   ([1, 1, -1], [1, 2, 5]),
                   ([3, -1, -1], [4, 5, 6]),
                   ([1, -1, -1], [2, 4, 5])]

        self.point_shapes = [square, square2]
        self.shapes = list(map(self.from_points_to_planes, self.point_shapes))

        self.rotation_angle_x = 0
        self.rotation_angle_y = 0
        self.rotation_angle_z = 0
        self.rotate()

        self.init_ui()

    def from_points_to_planes(self, point_shape):
        planes = np.array(list(set(filter(lambda p: p is not None, list(
            map(lambda p: self.get_plane_from_3_points(*p), combinations(point_shape, 3))))))).transpose()
        centroid = np.array(reduce(lambda a, x: a + x[0], np.array(point_shape), np.zeros(3)))/len(point_shape)

        return self.make_normal_vectior_point_outside(centroid, planes)

    def make_normal_vectior_point_outside(self, centroid, planes):
        result = []
        for plane in planes.transpose():
            if np.array(plane).dot(np.append (centroid, 1)) < 0:
                result.append(plane * -1)
            else:
                result.append(plane)
        return np.array(result).transpose()

    def in_hull(self, points, x):
        points = np.array(points)
        x = np.array(x)
        n_points = len(points)
        n_dim = len(x)
        c = np.zeros(n_points)
        A = np.r_[points.T, np.ones((1, n_points))]
        b = np.r_[x]
        lp = linprog(c, A_eq=A, b_eq=b)
        return lp.success

    def rotate(self):
        self.intersections_with_view_planes = []
        self.intersections_with_sides = []
        self.transformed_shapes = list(map(self.transform, self.shapes))
        self.lines_to_draw = list(chain(*map(lambda shape: self.find_shape_edges(shape), self.transformed_shapes)))

        self.visible_edges = []
        for shape in self.transformed_shapes:
            self.visible_edges.append(list(map(lambda edge: (edge, []), self.find_shape_edges(shape))))

        for i in range(len(self.transformed_shapes)):
            for j in range(len(self.transformed_shapes)):
                if i == j: continue
                for line1 in self.visible_edges[i]:
                    for line2 in self.visible_edges[j][:]:
                        t, intersection = self.view_plane_line_intercection(line1[0], line2[0])
                        if t:
                            self.intersections_with_view_planes.append(intersection)
                            line1[1].append(t)

        # t = 0, 1
        for i in range(len(self.transformed_shapes)):
            for j in range(len(self.transformed_shapes)):
                if i == j: continue
                planes = self.transformed_shapes[i].transpose()
                for plane in planes:
                    for line in self.visible_edges[j][:]:
                        intersection = self.isect_line_plane(line[0][0], np.array(line[0][0]) + np.array([0, 0, 1]),
                                                             plane)
                        if intersection is not None:
                            line_dot = np.dot(np.array(intersection) - np.array(line[0][0]), [0, 0, 1])
                            if line_dot > 0:
                                plane_dot = np.dot(planes, list(intersection) + [1])
                                if not any(map(lambda p: p < -0.01, plane_dot)):
                                    self.intersections_with_view_planes.append(intersection)
                                    line[1].append(0)

                        intersection = self.isect_line_plane(line[0][1], np.array(line[0][1]) + np.array([0, 0, 1]),
                                                             plane)
                        if intersection is not None:
                            line_dot = np.dot(np.array(intersection) - np.array(line[0][1]), [0, 0, 1])
                            if line_dot > 0:
                                plane_dot = np.dot(planes, list(intersection) + [1])
                                if not any(map(lambda p: p < -0.01, plane_dot)):
                                    self.intersections_with_view_planes.append(intersection)
                                    line[1].append(1)

        # p = 0
        for i in range(len(self.transformed_shapes)):
            for j in range(len(self.transformed_shapes)):
                if i == j: continue
                planes = self.transformed_shapes[i].transpose()
                for plane in planes:
                    for line in self.visible_edges[j][:]:
                        intersection = self.isect_line_plane(line[0][0], line[0][1], plane)
                        if intersection is not None:
                            intersection = intersection.tolist()
                            dot = np.dot(planes, intersection + [1])
                            if not any(map(lambda p: p < -0.01,
                                           dot)) and intersection not in self.intersections_with_sides:
                                self.intersections_with_sides.append(intersection)
                                t = np.linalg.norm((np.array(intersection) - np.array(line[0][0]))) / np.linalg.norm(
                                    (np.array(line[0][1]) - np.array(line[0][0])))
                                if 0 <= t <= 1:
                                    line[1].append(t)

        self.visible_intersection_points = []
        self.lines_to_draw = list(chain(*map(lambda edge: self.get_line_minmax(edge), chain(*self.visible_edges))))
        # intersection_edges = list(filter(lambda line: self.is_line_visible(line),
        #                                  permutations(self.visible_intersection_points, 2)))
        # self.lines_to_draw.extend(intersection_edges)
        self.update()

    def get_plane_from_3_points(self, point1, point2, point3):
        if not len(np.intersect1d(np.intersect1d(point1[1], point2[1]), point3[1])):
            return None
        x1, y1, z1 = point1[0]
        x2, y2, z2 = point2[0]
        x3, y3, z3 = point3[0]
        vector1 = [x2 - x1, y2 - y1, z2 - z1]
        vector2 = [x3 - x1, y3 - y1, z3 - z1]

        cross_product = [vector1[1] * vector2[2] - vector1[2] * vector2[1],
                         -1 * (vector1[0] * vector2[2] - vector1[2] * vector2[0]),
                         vector1[0] * vector2[1] - vector1[1] * vector2[0]]

        a = cross_product[0]
        b = cross_product[1]
        c = cross_product[2]
        d = - (cross_product[0] * x1 + cross_product[1] * y1 + cross_product[2] * z1)
        return (a / d, b / d, c / d, 1)

    def get_line_minmax(self, line):
        v = np.array(line[0][1]) - np.array(line[0][0])
        if len(line[1]) > 1:
            p1 = line[0][0] + min(line[1]) * v
            p2 = line[0][0] + max(line[1]) * v
            if np.any(list(map(lambda i: np.allclose(i, p1), self.intersections_with_sides))):
                self.visible_intersection_points.append(p1)
            if np.any(list(map(lambda i: np.allclose(i, p2), np.array(self.intersections_with_sides)))):
                self.visible_intersection_points.append(p2)
            result = [[line[0][0], p1], [p2, line[0][1]]]
            return list(filter(lambda p: not np.array_equal(p[0], p[1]), result))
        return [line[0]]

    def is_line_visible(self, line):
        # middle = np.append(self.get_middle_point(line), 1)
        # for shape in self.point_shapes:
        #     if (self.in_hull(np.array(list(map(lambda p: p[0], shape))), middle)):
        #         return False
        middle = np.append(self.get_middle_point(line), 1)
        for shape in self.transformed_shapes:
            planes = shape.transpose()
            dot = np.dot(planes, middle)
            if not any(map(lambda p: p < 0, dot)):
                return False
        return True

    def isect_line_plane(self, p0, p1, plane, epsilon=1):
        u = np.array(p1) - np.array(p0)
        dot = np.dot(plane[:3], u)
        plane = np.array(plane)
        if abs(dot) > epsilon:
            p_co = plane[:3] * -plane[3] / np.dot(plane[:3], plane[:3])
            w = np.array(p0) - np.array(p_co)
            fac = -np.dot(plane[:3], w) / dot
            u = u * fac
            intersection = p0 + u
            return intersection
        return None

    def get_middle_point(self, line):
        A = np.array(line[0])
        B = np.array(line[1])
        return ((B - A) / 2) + A

    def view_plane_line_intercection(self, view_line, line):
        A = np.array(view_line[0])
        B = np.array(view_line[1])
        D = np.array([0, 0, 1])
        C = np.array(line[1]) - np.array(line[0])
        matrix = np.array([B - A, D, -C]).transpose()

        right_handside = np.array(np.array(line[0]) - A)
        try:
            t, p, s = np.linalg.solve(matrix, right_handside)
            if (0 <= t <= 1 and p >= 0 and 0 <= s <= 1):
                new = (np.array(line[0]) + C * s)
                return t, new.tolist()
        except:
            return None, None
        return None, None

    def shape_side_line_intersection(self, plane, line):
        px, py, pz = line[0]
        qx, qy, qz = line[1]
        a, b, c, d = plane
        tDenom = a * (qx - px) + b * (qy - py) + c * (qz - pz)
        if (tDenom == 0):
            return None
        t = - (a * px + b * py + c * pz + d) / tDenom
        return [(px + t * (qx - px)), (py + t * (qy - py)), (pz + t * (qz - pz))]

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
                if p1 == p3 or p1 == p3 or p2 == p3:
                    continue
                c = 0
                if np.dot(p1, [0, 0, -1, 0]) <= 0: c += 1
                if np.dot(p2, [0, 0, -1, 0]) <= 0: c += 1
                if np.dot(p3, [0, 0, -1, 0]) <= 0: c += 1
                if c == 3:
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

    def distance(self, point1, point2):
        p = np.array(point1) - np.array(point2)
        return math.sqrt(np.dot(p, p))

    def init_ui(self):
        self.setWindowTitle('Fifth Task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        font = QFont()
        font.setPixelSize(10)
        qp.setFont(font)
        self.draw_shape(qp)
        qp.end()

    def draw_shape(self, qp: QPainter):
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        # helpers
        qp.drawText(QPoint(0, 10),
                    'rotaion: ' + str(np.array([self.rotation_angle_x, self.rotation_angle_y, self.rotation_angle_z])))
        for line in self.lines_to_draw:
            qp.drawLine(self.plane_to_screen(line[0]), self.plane_to_screen(line[1]))
            # helpers
            qp.drawText(self.plane_to_screen(line[0]), str(np.array(line[0])))
            qp.drawText(self.plane_to_screen(line[1]), str(np.array(line[1])))

        # helpers
        qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        for point in self.intersections_with_view_planes:
            qp.drawPoint(self.plane_to_screen(point))
            qp.drawText(self.plane_to_screen(point), str(np.array(point)))

        qp.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        for point in self.intersections_with_sides:
            qp.drawPoint(self.plane_to_screen(point))
            qp.drawText(self.plane_to_screen(point), str(np.array(point)))

    def plane_to_screen(self, v):
        xp, yp = self.front_projection(v)
        xx = round((xp - self.x1) * self.geometry().width() / (self.x2 - self.x1))
        yy = self.geometry().height() - round((yp - self.y1) * self.geometry().height() / (self.y2 - self.y1))
        return QPoint(xx, yy)

    def front_projection(self, v):
        return v[0], v[1]

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

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_S:
            self.rotation_angle_x += 0.1
        elif event.key() == QtCore.Qt.Key_W:
            self.rotation_angle_x -= 0.1

        elif event.key() == QtCore.Qt.Key_D:
            self.rotation_angle_y += 0.1
        elif event.key() == QtCore.Qt.Key_A:
            self.rotation_angle_y -= 0.1

        elif event.key() == QtCore.Qt.Key_Q:
            self.rotation_angle_z += 0.1
        elif event.key() == QtCore.Qt.Key_E:
            self.rotation_angle_z -= 0.1
        else:
            return
        self.rotate()


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

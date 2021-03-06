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

np.set_printoptions(precision=2)
EPSILON = 0.000001

class FifthTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 800, 800)

        self.x1 = -4
        self.x2 = 4
        self.y1 = -4
        self.y2 = 4

        square = [([1.2, 1.2, 1.2], [0, 2, 5]),
                  ([-1.2, 1.2, 1.2], [0, 1, 2]),
                  ([1.2, -1.2, 1.2], [2, 3, 5]),
                  ([1.2, 1.2, -1.2], [0, 4, 5]),
                  ([-1.2, -1.2, 1.2], [1, 2, 3]),
                  ([-1.2, 1.2, -1.2], [0, 1, 4]),
                  ([1.2, -1.2, -1.2], [3, 4, 5]),
                  ([-1.2, -1.2, -1.2], [1, 3, 4])]

        tetra = [([3, 0, 0], [0, 1, 2]),
                 ([0, 0.5, 0.5], [0, 1, 3]),
                 ([0, -0.5, 0.5], [0, 2, 3]),
                 ([0, 0.5, -0.5], [1, 2, 3])]

        square2 = [([1, 1.5, 1], [0, 2, 5]),
                  ([-1, 1.5, 1], [0, 1, 2]),
                  ([1, -1.5, 1], [2, 3, 5]),
                  ([1, 1.5, -1], [0, 4, 5]),
                  ([-1, -1.5, 1], [1, 2, 3]),
                  ([-1, 1.5, -1], [0, 1, 4]),
                  ([1, -1.5, -1], [3, 4, 5]),
                  ([-1, -1.5, -1], [1, 3, 4])]

        square3 = [([2, 1, 1.5], [0, 2, 5]),
                  ([0, 1, 1.5], [0, 1, 2]),
                  ([2, -1, 1.5], [2, 3, 5]),
                  ([2, 1, -1.5], [0, 4, 5]),
                  ([0, -1, 1.5], [1, 2, 3]),
                  ([0, 1, -1.5], [0, 1, 4]),
                  ([2, -1, -1.5], [3, 4, 5]),
                  ([0, -1, -1.5], [1, 3, 4])]

        self.point_shapes = [square2, square3, square, tetra]

        self.rotation_angle_x = 0
        self.rotation_angle_y = 0
        self.rotation_angle_z = 0
        self.redraw()

        self.init_ui()

    def make_normal_vectior_point_outside(self, centroid, plane):
        if np.array(plane).dot(np.append(centroid, 1)) < EPSILON:
            return (plane * -1)
        return plane

    def redraw(self):
        self.intersections_with_view_planes = []
        self.transformed_point_shapes = []
        self.lines_to_draw = []
        self.black_points = []
        self.visible_edges = [[] for _ in range(len(self.point_shapes))]
        self.transformed_plane_shapes = [[] for _ in range(len(self.point_shapes))]
        self.visible_plane_shapes = [[] for _ in range(len(self.point_shapes))]
        self.intersections_with_sides_shapes = [[] for _ in range(len(self.point_shapes))]

        for p_shape in self.point_shapes:
            t = list(map(self.transform, p_shape))
            self.transformed_point_shapes.append(list(map(lambda p: (p[0][:3], p[1]), t)))


        for index, p_shape in enumerate(self.transformed_point_shapes):
            plane_ids = set().union(*list(map(lambda p: p[1], p_shape)))
            centroid = np.array(reduce(lambda a, x: a + x[0], np.array(p_shape), np.zeros(3))) / len(p_shape)
            for id in plane_ids:
                plane_points = list(filter(lambda p: id in p[1], p_shape))
                plane = np.array(self.get_plane_from_3_points(*[p[0] for p in plane_points]))
                plane = self.make_normal_vectior_point_outside(centroid, plane)
                if np.dot(plane, [0, 0, -1, 0]) > EPSILON:
                    self.visible_plane_shapes[index].append(plane)
                    for p1, p2 in combinations(plane_points, 2):
                        if len(set(p1[1]).intersection(p2[1]).difference(list([id]))):
                            self.visible_edges[index].append([[p1[0][:3], p2[0][:3]], []])
                self.transformed_plane_shapes[index].append(plane)
            self.transformed_plane_shapes[index] = np.array(self.transformed_plane_shapes[index]).transpose()

        # p = 0
        for i in range(len(self.point_shapes)):
            for j in range(len(self.point_shapes)):
                if i == j: continue
                planes = np.array(self.transformed_plane_shapes[i]).transpose()
                for line in self.visible_edges[j][:]:
                    for plane in planes:
                        p1, p2 = line[0]
                        intersection, t = self.linePlaneIntersection(p1, p2, plane, [0 + EPSILON*2, 1 - EPSILON*2])
                        if intersection is not None:
                            dot = np.dot(list(filter(lambda p: not np.array_equal(plane, p), planes.tolist())), np.append(intersection, 1))
                            if not any(map(lambda p: p < -EPSILON, dot)):
                                self.intersections_with_sides_shapes[j].append(intersection)
                                line[1].append(t)

        # 0 < t < 1
        for i in range(len(self.point_shapes)):
            for j in range(len(self.point_shapes)):
                if i == j: continue
                for line1 in self.visible_edges[i]:
                    for line2 in self.visible_edges[j][:]:
                        t, intersection = self.view_plane_line_intercection(line1[0], line2[0])
                        if t:
                            # self.intersections_with_view_planes.append(intersection)
                            line1[1].append(t)

        # # # adding intersection edges
        self.visible_edges.append(list(map(lambda line: (line, []),
                                           list(filter(lambda line: self.is_line_visible(line),
                                                       permutations(chain(*self.intersections_with_sides_shapes), 2))))))

        # t = 0, 1
        for i in range(len(self.point_shapes)):
            for j in range(len(self.point_shapes)+1):
                if i == j: continue
                planes = np.array(self.transformed_plane_shapes[i]).transpose()
                for plane in planes:
                    for line in self.visible_edges[j][:]:
                        p1, p2 = line[0]

                        intersection, t = self.linePlaneIntersection(p1, p1 + np.array([0, 0, 1]), plane, [0, float('inf')])
                        if intersection is not None and abs(t) > EPSILON:
                            dot = np.dot(list(filter(lambda p: not np.array_equal(plane, p), planes.tolist())), np.append(intersection, 1))
                            if not any(map(lambda p: p < EPSILON, dot)):
                                self.intersections_with_view_planes.append(intersection)
                                line[1].append(0)

                        intersection, t = self.linePlaneIntersection(p2, p2 + np.array([0, 0, 1]), plane, [0, float('inf')])
                        if intersection is not None and abs(t) > EPSILON:
                            dot = np.dot(list(filter(lambda p: not np.array_equal(plane, p), planes.tolist())),
                                         np.append(intersection, 1))
                            if not any(map(lambda p: p < EPSILON, dot)):
                                self.intersections_with_view_planes.append(intersection)
                                line[1].append(1)




        self.lines_to_draw = list(chain(*map(lambda edge: self.get_line_minmax(edge), chain(*self.visible_edges))))

        self.update()

    def linePlaneIntersection(self, p1, p2, plane, interval):
        # https://stackoverflow.com/a/7170101/7868408
        plane = np.array(plane)
        normal = plane[:3]
        if plane[2]:
            coord = np.array([0,0, -plane[3]/plane[2]])
        elif plane[1]:
            coord = np.array([0, -plane[3] / plane[1], 0])
        else:
            coord = np.array([-plane[3] / plane[0], 0, 0])
        ray = np.array(p2) - np.array(p1)
        d = np.dot(normal, coord)
        if abs(np.dot(normal, ray)) < EPSILON:
            return None, None
        x = (d - np.dot(normal, p1))/np.dot(normal, ray)

        intersection = p1 + ray*x
        if interval[0] - EPSILON <= x <= interval[1] + EPSILON:
            return intersection, x
        return None, None

    def normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm

    def get_plane_from_3_points(self, point1, point2, point3, *ignored):
        x1, y1, z1 = point1
        x3, y3, z3 = point3
        x2, y2, z2 = point2
        vector1 = [x2 - x1, y2 - y1, z2 - z1]
        vector2 = [x3 - x1, y3 - y1, z3 - z1]

        cross_product = [vector1[1] * vector2[2] - vector1[2] * vector2[1],
                         -1 * (vector1[0] * vector2[2] - vector1[2] * vector2[0]),
                         vector1[0] * vector2[1] - vector1[1] * vector2[0]]

        a = cross_product[0]
        b = cross_product[1]
        c = cross_product[2]
        d = - (cross_product[0] * x1 + cross_product[1] * y1 + cross_product[2] * z1)


        return (a, b, c, d)

    def get_line_minmax(self, line):
        v = np.array(line[0][1]) - np.array(line[0][0])
        if len(set(line[1])) > 1:
            p1 = line[0][0] + min(line[1]) * v
            p2 = line[0][0] + max(line[1]) * v
            result = [[line[0][0], p1], [p2, line[0][1]]]
            return list(filter(lambda p: not np.array_equal(p[0], p[1]), result))
        elif len(set(line[1])) == 1:
            return []
        return [line[0]]

    def is_line_visible(self, line):
        middle = np.array(self.get_middle_point(line))
        for shape in self.transformed_plane_shapes:
            planes = np.array(shape).transpose()
            dot = np.dot(planes, np.append(middle, 1))
            if all(map(lambda p: p > EPSILON, dot)):
                return False
        for plane in chain(*self.visible_plane_shapes):
            intersection, t = self.linePlaneIntersection(middle, middle + np.array([0, 0, 1]), plane, [2*EPSILON+0, float('inf')])
            if intersection is not None:
                dot = np.dot(list(filter(lambda p: not np.array_equal(plane, p), planes.tolist())),
                             np.append(intersection, 1))
                if not any(map(lambda p: p < EPSILON, dot)):
                    return False
        return True


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
                return t, new
        except:
            return None, None
        return None, None

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
            # qp.drawText(self.plane_to_screen(line[0]), str(np.array(line[0])))
            # qp.drawText(self.plane_to_screen(line[1]), str(np.array(line[1])))

        # helpers
        # qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        # for point in self.intersections_with_view_planes:
        #     qp.drawPoint(self.plane_to_screen(point))
        #     qp.drawText(self.plane_to_screen(point), str(np.array(point)))

        # qp.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        # for point in chain(*self.intersections_with_sides_shapes):
        #     qp.drawPoint(self.plane_to_screen(point))
        #     qp.drawText(self.plane_to_screen(point), str(np.array(point)))

        # qp.setPen(QPen(Qt.black, 3, Qt.SolidLine))
        # for point in self.black_points:
        #     qp.drawPoint(self.plane_to_screen(point))
        #     qp.drawText(self.plane_to_screen(point), str(np.array(point)))

    def plane_to_screen(self, v):
        xp, yp = self.front_projection(v)
        xx = round((xp - self.x1) * self.geometry().width() / (self.x2 - self.x1))
        yy = self.geometry().height() - round((yp - self.y1) * self.geometry().height() / (self.y2 - self.y1))
        return QPoint(xx, yy)

    def front_projection(self, v):
        return v[0], v[1]

    def transform(self, point):
        m = point[0]
        if len(m) == 3:
            m = np.append(m, [0])
        return self.rotation_z(self.rotation_y(self.rotation_x(m))), point[1]

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
        self.redraw()


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

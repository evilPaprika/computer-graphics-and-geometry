import itertools
import math

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


class FirstTask(QWidget):
    def __init__(self):
        super().__init__()

        self.a = 1
        self.b = 2

        self.focus = 0, self.b + 1 / (4 * self.a)
        self.vertex = 0, self.function(0)
        self.decart_focus = self.backwards_substitution(*self.focus)
        self.decart_vertex = self.backwards_substitution(*self.vertex)
        print('substituted focus: ', self.focus)
        print('substituted vertex: ', self.vertex)
        print('decart focus: ', self.decart_focus)
        print('decart vertex: ', self.decart_vertex)

        self.directrix_zero = self.backwards_substitution(0, self.b - 1 / (4 * self.a))
        self.directrix_b = self.directrix_zero[1] - self.directrix_zero[0]  # смещение уравнения прямой директрисы

        self.ymax = 5
        self.ymin = -5

        self.start = -5
        self.end = 5

        self.function_upper_bound = 1000
        self.function_lower_bound = -1000

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 1000, 600)
        self.setWindowTitle('First task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        # self.find_function_min_and_max()
        self.draw_axes(qp)
        self.draw_function(qp)
        self.draw_parabola_helpers(qp)
        qp.end()

    def draw_parabola_helpers(self, qp):
        # фокус
        qp.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        qp.drawPoint(*self.coords_to_screen_point(*self.decart_focus))
        # вершина параболы
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
        print(*self.coords_to_screen_point(*self.decart_vertex))
        qp.drawPoint(*self.coords_to_screen_point(*self.decart_vertex))
        # точка директрисы
        qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        qp.drawPoint(*self.coords_to_screen_point(*self.directrix_zero))
        # директриса
        qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        qp.drawLine(*self.coords_to_screen_point(self.start, self.start + self.directrix_b),
                    *self.coords_to_screen_point(self.ymax - self.directrix_b, self.ymax))

    def coords_to_screen_point(self, x, y):
        return round((x - self.start) * self.geometry().width() / (self.end - self.start)), \
               round((y - self.ymax) * self.geometry().height() / (self.ymin - self.ymax))

    def screen_point_to_coords(self, x, y):
        return x * (self.end - self.start) / self.geometry().width() + self.start, \
               y * (self.ymin - self.ymax) / self.geometry().height() + self.ymax

    def substitution(self, x, y):
        return x + y, y

    def backwards_substitution(self, u, v):
        return u - v, v

    def error_size(self, u, v):
        distance_to_disectrix = abs(u + v + self.directrix_b) / (math.sqrt(2))
        distance_to_focus = math.sqrt((self.focus[0] - u) ** 2 + (self.focus[1] - v) ** 2)
        print(abs(distance_to_disectrix - distance_to_focus))
        return abs(distance_to_disectrix - distance_to_focus)

    def get_adjacent_points(self, xx, yy):
        connected_moves = list(filter(lambda m: m != (0, 0), itertools.product([-1, 0, 1], repeat=2)))

        return list(filter(lambda point: self.fits_on_screen(*point) and point not in self.visited_points,
                      [(move[0] + xx, move[1] + yy) for move in connected_moves]))

    def get_best_point(self, old_point):
        return min(list(map(lambda point: (self.error_size(*self.substitution(*self.screen_point_to_coords(*point))), point),
                     self.get_adjacent_points(*old_point))), key=lambda x: x[0])[1]

    def draw_function(self, qp):
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        self.visited_points = [self.coords_to_screen_point(*self.decart_vertex)]
        for i in range(100):
            new_point = self.get_best_point(self.visited_points[-1])
            print(new_point)
            qp.drawPoint(*new_point)
            self.visited_points.append(new_point)

    def find_function_min_and_max(self):
        ymin = ymax = self.function(self.start)
        for xx in range(self.geometry().width()):
            x = xx * (self.end - self.start) / self.geometry().width() + self.start
            y = self.function(x)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
        self.ymin = max(self.function_lower_bound, round(ymin))
        self.ymax = min(self.function_upper_bound, round(ymax))

    def fits_on_screen(self, xx, yy):
        return 0 <= xx < self.geometry().width() and 0 <= yy < self.geometry().height()

    def draw_axes(self, qp):
        qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        xx0, yy0 = self.coords_to_screen_point(0, 0)
        qp.drawLine(xx0, 0, xx0, self.geometry().height())
        qp.drawLine(0, yy0, self.geometry().width(), yy0)
        self.draw_axes_notches(qp, xx0, yy0)

    def draw_axes_notches(self, qp, xx0, yy0):
        qp.setBrush(QBrush(Qt.SolidPattern))
        qp.setFont(QFont('Decorative', 7))
        step = max(1, round(self.screen_point_to_coords(32, 0)[0] - self.screen_point_to_coords(0, 0)[0]))
        for x in range(step, max(abs(self.start), abs(self.end)), step):
            xx_right, yy = self.coords_to_screen_point(x, 0)
            xx_left, yy = self.coords_to_screen_point(-x, 0)
            qp.drawLine(xx_right, yy - 2, xx_right, yy + 2)
            qp.drawLine(xx_left, yy - 2, xx_left, yy + 2)
            qp.drawText(QRect(xx_right - 10, yy + 10, 20, 20), Qt.AlignCenter, str(x))
            qp.drawText(QRect(xx_left - 10, yy + 10, 20, 20), Qt.AlignCenter, str(-x))

        step = max(1, round(self.screen_point_to_coords(0, 0)[1] - self.screen_point_to_coords(0, 32)[1]))
        for y in range(step, max(abs(self.ymin), abs(self.ymax)), step):
            xx, yy_up = self.coords_to_screen_point(0, y)
            xx, yy_down = self.coords_to_screen_point(0, -y)
            qp.drawLine(xx - 2, yy_up, xx + 2, yy_up)
            qp.drawLine(xx - 2, yy_down, xx + 2, yy_down)
            qp.drawText(QRect(xx + 10, yy_up - 10, 20, 20), Qt.AlignCenter, str(y))
            qp.drawText(QRect(xx + 10, yy_down - 10, 20, 20), Qt.AlignCenter, str(-y))

        qp.drawPolygon(QPolygon([QPoint(self.geometry().width() - 8, yy0 + 3),
                                 QPoint(self.geometry().width() - 8, yy0 - 3),
                                 QPoint(self.geometry().width(), yy0)]))
        qp.drawPolygon(QPolygon([QPoint(xx0 - 3, 0 + 8),
                                 QPoint(xx0 + 3, 0 + 8),
                                 QPoint(xx0, 0)]))

    def function(self, u):
        return self.a * u ** 2 + self.b


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstTask()
    sys.exit(app.exec_())

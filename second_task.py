import itertools
import math
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


class SecondTask(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 600, 600)

        self.pf = PointFactory(self)

        self.a = 1
        self.b = 2

        self.function_upper_bound = 1000
        self.function_lower_bound = -1000

        self.ymax = 6
        self.ymin = -1

        self.start = -6
        self.end = 1

        self.focus = self.pf.from_substituted(0, self.b + 1 / (4 * self.a))
        self.vertex = self.pf.from_substituted(0, self.function(0))
        self.directrix_zero = self.pf.from_substituted(0, self.b - 1 / (4 * self.a))
        self.directrix_b = self.directrix_zero.v - self.directrix_zero.u  # смещение уравнения прямой директрисы

        print('focus:', self.focus)
        print('vertex:', self.vertex)
        print('directrix:', self.directrix_zero)

        self.directrix_zero = self.pf.from_substituted(0, self.b - 1 / (4 * self.a))
        self.directrix_b = self.directrix_zero.y - self.directrix_zero.x  # смещение уравнения прямой директрисы

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Second task')
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_axes(qp)
        self.draw_function(qp)
        self.draw_parabola_helpers(qp)
        qp.end()

    def draw_parabola_helpers(self, qp):
        # фокус
        qp.setPen(QPen(Qt.green, 3, Qt.SolidLine))
        qp.drawPoint(*self.focus.screen())
        # вершина параболы
        qp.setPen(QPen(Qt.blue, 3, Qt.SolidLine))
        qp.drawPoint(*self.vertex.screen())
        # точка директрисы
        qp.setPen(QPen(Qt.red, 3, Qt.SolidLine))
        qp.drawPoint(*self.directrix_zero.screen())
        # директриса
        qp.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        qp.drawLine(*self.pf.from_cartesian(self.start, self.start + self.directrix_b).screen(),
                    *self.pf.from_cartesian(self.ymax - self.directrix_b, self.ymax).screen())

    def error_size(self, u, v):
        distance_to_disectrix = abs(v + 1 / (4 * self.a) - self.b)
        distance_to_focus = math.sqrt((self.focus.u - u) ** 2 + (self.focus.v - v) ** 2)
        return abs(distance_to_disectrix - distance_to_focus)

    def get_best_point(self, old_point):
        return \
            min(list(
                map(lambda point: (self.error_size(*point.substituted()), point),
                    old_point.neighbors())), key=lambda x: x[0], default=(None, None))[1]

    def draw_function(self, qp):
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        self.visited_points = []
        branch_start_1 = self.get_best_point(self.vertex)
        self.draw_parabola_branch(qp, branch_start_1)
        self.visited_points = [branch_start_1]
        branch_start_2 = self.get_best_point(self.vertex)
        self.draw_parabola_branch(qp, branch_start_2)

    def draw_parabola_branch(self, qp, branch_start):
        self.visited_points = [branch_start, self.vertex]
        while True:
            new_point = self.get_best_point(self.visited_points[-1])
            if not new_point:
                break
            qp.drawPoint(*new_point.screen())
            self.visited_points.append(new_point)

    def draw_axes(self, qp):
        qp.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        origin = self.pf.from_cartesian(0, 0)
        qp.drawLine(origin.xx, 0, origin.xx, self.geometry().height())
        qp.drawLine(0, origin.yy, self.geometry().width(), origin.yy)
        self.draw_axes_notches(qp, origin)

    def draw_axes_notches(self, qp, origin):
        qp.setBrush(QBrush(Qt.SolidPattern))
        qp.setFont(QFont('Decorative', 7))
        step = max(1, round(self.pf.from_screen(32, 0).x - self.pf.from_screen(0, 0).x))

        for x in range(step, max(abs(self.start), abs(self.end)), step):
            xx_right, yy = self.pf.from_cartesian(x, 0).screen()
            xx_left, yy = self.pf.from_cartesian(-x, 0).screen()
            qp.drawLine(xx_right, yy - 2, xx_right, yy + 2)
            qp.drawLine(xx_left, yy - 2, xx_left, yy + 2)
            qp.drawText(QRect(xx_right - 10, yy + 10, 20, 20), Qt.AlignCenter, str(x))
            qp.drawText(QRect(xx_left - 10, yy + 10, 20, 20), Qt.AlignCenter, str(-x))

        step = max(1, round(self.pf.from_screen(0, 0).y - self.pf.from_screen(0, 32).y))
        for y in range(step, max(abs(self.ymin), abs(self.ymax)), step):
            xx, yy_up = self.pf.from_cartesian(0, y).screen()
            xx, yy_down = self.pf.from_cartesian(0, -y).screen()
            qp.drawLine(xx - 2, yy_up, xx + 2, yy_up)
            qp.drawLine(xx - 2, yy_down, xx + 2, yy_down)
            qp.drawText(QRect(xx + 10, yy_up - 10, 20, 20), Qt.AlignCenter, str(y))
            qp.drawText(QRect(xx + 10, yy_down - 10, 20, 20), Qt.AlignCenter, str(-y))

        qp.drawPolygon(QPolygon([QPoint(self.geometry().width() - 8, origin.yy + 3),
                                 QPoint(self.geometry().width() - 8, origin.yy - 3),
                                 QPoint(self.geometry().width(), origin.yy)]))
        qp.drawPolygon(QPolygon([QPoint(origin.xx - 3, 0 + 8),
                                 QPoint(origin.xx + 3, 0 + 8),
                                 QPoint(origin.xx, 0)]))

    def function(self, u):
        return self.a * u ** 2 + self.b


class PointFactory:
    def __init__(self, base):
        self.base = base

    def from_screen(self, xx, yy):
        return Point('screen', xx, yy, self.base)

    def from_cartesian(self, x, y):
        return Point('cartesian', x, y, self.base)

    def from_substituted(self, u, v):
        return Point('substituted', u, v, self.base)


class Point:
    def __init__(self, space, x, y, base):
        self.base = base
        if space == 'screen':
            self._x, self._y = self._screen_to_cartesian(x, y)
        elif space == 'cartesian':
            self._x, self._y = x, y
        elif space == 'substituted':
            self._x, self._y = self._substituted_to_cartesian(x, y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def xx(self):
        return round((self.x - self.base.start) * self.base.geometry().width() / (
                self.base.end - self.base.start))

    @property
    def yy(self):
        return round(
            (self.y - self.base.ymax) * self.base.geometry().height() / (
                    self.base.ymin - self.base.ymax))

    @property
    def u(self):
        return self.x + self.y

    @property
    def v(self):
        return self.y

    def neighbors(self):
        connected_moves = list(filter(lambda m: m != (0, 0), itertools.product([-1, 0, 1], repeat=2)))
        result = []
        for point in [self.base.pf.from_screen(move[0] + self.xx, move[1] + self.yy) for move in connected_moves]:
            if point not in self.base.visited_points:
                result.append(point)
            if not self.fits_on_screen(point):
                break
        else:
            return result
        return []

    def fits_on_screen(self, point):
        return 0 <= point.xx < self.base.geometry().width() and 0 <= point.yy < self.base.geometry().height()

    def screen(self):
        return self.xx, self.yy

    def cartesian(self):
        return self.x, self.y

    def substituted(self):
        return self.u, self.v

    def _screen_to_cartesian(self, x, y):
        return x * (self.base.end - self.base.start) / self.base.geometry().width() + self.base.start, \
               y * (self.base.ymin - self.base.ymax) / self.base.geometry().height() + self.base.ymax

    def _substituted_to_cartesian(self, u, v):
        return u - v, v

    def __eq__(self, o) -> bool:
        return self.xx == o.xx and self.yy == o.yy

    def __str__(self):
        return str(f"screen: ({self.xx}, {self.yy}) cartesian: ({self.x}, {self.y}) substituted: ({self.u}, {self.v})")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SecondTask()
    sys.exit(app.exec_())

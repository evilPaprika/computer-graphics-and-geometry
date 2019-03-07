from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPainter, QPen, QPolygon, QBrush, QFont
from PyQt5.QtCore import Qt, QPoint, QRect
import sys


class FirstTask(QWidget):
    def __init__(self, function):
        super().__init__()

        self.start = -20
        self.end = 20
        self.function = function

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
        self.find_function_min_and_max()
        self.draw_axes(qp)
        self.draw_function(qp)
        qp.end()

    def coords_to_screen_point(self, x, y):
        return round((x - self.start) * self.geometry().width() / (self.end - self.start)), \
               round((y - self.ymax) * self.geometry().height() / (self.ymin - self.ymax)) - 30

    def screen_point_to_coords(self, x, y):
        return x * (self.end - self.start) / self.geometry().width() + self.start, \
               y * (self.ymin - self.ymax) / self.geometry().height() + self.ymax

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

    def draw_function(self, qp):
        qp.setPen(QPen(Qt.blue, 1, Qt.SolidLine))
        prev_point = QPoint(*self.coords_to_screen_point(self.start, self.function(self.start)))
        for xx in range(1, self.geometry().width()):
            x, _ = self.screen_point_to_coords(xx, 0)
            _, yy = self.coords_to_screen_point(0, self.function(x))
            new_point = QPoint(xx, yy)
            qp.drawLine(prev_point, new_point)
            prev_point = new_point

    def find_function_min_and_max(self):
        ymin = ymax = self.function(self.start)
        for xx in range(self.geometry().width()):
            x = xx * (self.end - self.start) / self.geometry().width() + self.start
            y = self.function(x)
            ymin = min(ymin, y)
            ymax = max(ymax, y)
        self.ymin = max(self.function_lower_bound, round(ymin))
        self.ymax = min(self.function_upper_bound, round(ymax))


def foo(x):
    return x ** 2 - 10


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FirstTask(foo)
    sys.exit(app.exec_())

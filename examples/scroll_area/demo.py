# coding:utf-8
import sys
from PyQt6.QtCore import QEasingCurve, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel
from qfluentwidgets import SmoothScrollArea


class Demo(SmoothScrollArea):

    def __init__(self):
        super().__init__()
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap("resource/shoko.jpg"))

        # customize scroll animation
        self.setScrollAnimation(Qt.Orientation.Vertical, 400, QEasingCurve.Type.OutQuint)
        self.setScrollAnimation(Qt.Orientation.Horizontal, 400, QEasingCurve.Type.OutQuint)

        self.horizontalScrollBar().setValue(1900)
        self.setWidget(self.label)
        self.resize(960, 640)

        with open('resource/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Demo()
    w.show()
    app.exec()
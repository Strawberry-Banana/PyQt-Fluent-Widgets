# coding:utf-8
from PyQt6.QtCore import (QEvent, Qt, QPropertyAnimation, pyqtProperty, QEasingCurve,
                          QParallelAnimationGroup, QRect, QSize, QPoint, QRectF)
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtWidgets import QFrame, QWidget, QAbstractButton, QApplication
from PyQt6.QtSvg import QSvgRenderer

from ...common.config import qconfig
from ...common.style_sheet import setStyleSheet
from .setting_card import SettingCard
from .setting_card import SettingIconFactory as SIF
from ..layout.v_box_layout import VBoxLayout


class ExpandButton(QAbstractButton):
    """ Expand button """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(30, 30)
        self.__angle = 0
        self.isHover = False
        self.isPressed = False
        self.iconPath = SIF.create(SIF.ARROW_DOWN)
        self.rotateAni = QPropertyAnimation(self, b'angle', self)
        self.clicked.connect(self.__onClicked)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing |
                               QPainter.RenderHint.SmoothPixmapTransform)
        painter.setPen(Qt.PenStyle.NoPen)

        # draw background
        r = 255 if qconfig.theme == 'dark' else 0
        if self.isPressed:
            color = QColor(r, r, r, 10)
        elif self.isHover:
            color = QColor(r, r, r, 14)
        else:
            color = Qt.GlobalColor.transparent

        painter.setBrush(color)
        painter.drawRoundedRect(self.rect(), 4, 4)

        # draw icon
        painter.translate(self.width()//2, self.height()//2)
        painter.rotate(self.__angle)
        renderer = QSvgRenderer(self.iconPath, self)
        renderer.render(painter, QRectF(-6, -6, 9.6, 9.6))

    def enterEvent(self, e):
        self.setHover(True)

    def leaveEvent(self, e):
        self.setHover(False)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.setPressed(True)

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.setPressed(False)

    def setHover(self, isHover: bool):
        self.isHover = isHover
        self.update()

    def setPressed(self, isPressed: bool):
        self.isPressed = isPressed
        self.update()

    def __onClicked(self):
        self.rotateAni.setEndValue(180 if self.angle < 180 else 0)
        self.rotateAni.setDuration(200)
        self.rotateAni.start()

    def getAngle(self):
        return self.__angle

    def setAngle(self, angle):
        self.__angle = angle
        self.update()

    angle = pyqtProperty(float, getAngle, setAngle)


class ExpandSettingCard(QFrame):
    """ Expandable setting card """

    def __init__(self, iconPath: str, title: str, content: str = None, parent=None):
        super().__init__(parent=parent)
        self.isExpand = False
        self.expandButton = ExpandButton(self)
        self.view = QFrame(self)
        self.card = SettingCard(iconPath, title, content, self)
        self.viewLayout = VBoxLayout(self.view)

        # expand animation
        self.aniGroup = QParallelAnimationGroup(self)
        self.slideAni = QPropertyAnimation(self.view, b'pos', self)
        self.expandAni = QPropertyAnimation(self, b'geometry', self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setMinimumHeight(self.card.height())
        self.view.hide()

        # initialize expand animation
        self.aniGroup.addAnimation(self.expandAni)
        self.aniGroup.addAnimation(self.slideAni)
        self.slideAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.expandAni.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.slideAni.setDuration(200)
        self.expandAni.setDuration(200)

        # initialize style sheet
        self.view.setObjectName('view')
        self.setProperty('isExpand', False)
        setStyleSheet(self.card, 'expand_setting_card')
        setStyleSheet(self, 'expand_setting_card')

        self.card.installEventFilter(self)
        self.aniGroup.finished.connect(self.__onAniFinished)
        self.expandButton.clicked.connect(self.toggleExpand)

    def addWidget(self, widget: QWidget):
        """ add widget to tail """
        self.card.hBoxLayout.addWidget(widget, 0, Qt.AlignmentFlag.AlignRight)
        self.card.hBoxLayout.addSpacing(19)
        self.card.hBoxLayout.addWidget(self.expandButton, 0, Qt.AlignmentFlag.AlignRight)
        self.card.hBoxLayout.addSpacing(8)

    def setExpand(self, isExpand: bool):
        """ set the expand status of card """
        if self.isExpand == isExpand:
            return

        # update style sheet
        self.isExpand = isExpand
        self.setProperty('isExpand', isExpand)
        self.setStyle(QApplication.style())

        # start expand animation
        ch, vh = self.card.height(), self.view.height()
        if isExpand:
            self.expandAni.setStartValue(self.geometry())
            self.expandAni.setEndValue(
                QRect(self.pos(), QSize(self.width(), ch+vh)))
            self.slideAni.setStartValue(QPoint(0, ch - vh))
            self.slideAni.setEndValue(QPoint(0, ch))
            self.view.show()
        else:
            self.expandAni.setStartValue(self.geometry())
            self.expandAni.setEndValue(QRect(self.pos(), self.card.size()))
            self.slideAni.setStartValue(QPoint(0, ch))
            self.slideAni.setEndValue(QPoint(0, ch - vh))

        self.aniGroup.start()

    def toggleExpand(self):
        """ toggle expand status """
        self.setExpand(not self.isExpand)

    def resizeEvent(self, e):
        self.card.resize(self.width(), self.card.height())
        self.view.resize(self.width(), self.view.height())

    def eventFilter(self, obj, e):
        if obj is self.card:
            if e.type() == QEvent.Type.Enter:
                self.expandButton.setHover(True)
            elif e.type()==QEvent.Type.Leave:
                self.expandButton.setHover(False)
            elif e.type() == QEvent.Type.MouseButtonPress and e.button() == Qt.MouseButton.LeftButton:
                self.expandButton.setPressed(True)
            elif e.type() == QEvent.Type.MouseButtonRelease and e.button() == Qt.MouseButton.LeftButton:
                self.expandButton.setPressed(False)
                self.expandButton.click()

        return super().eventFilter(obj, e)

    def __onAniFinished(self):
        """ expand animation finished slot """
        if not self.isExpand:
            self.view.hide()

    def _adjustViewSize(self):
        """ adjust view size """
        h = sum(i.height() for i in self.viewLayout.widgets)
        spacing = (len(self.viewLayout.widgets) - 1) * \
            self.viewLayout.spacing()
        margin = self.viewLayout.contentsMargins()
        h = h + margin.top() + margin.bottom() + spacing
        self.view.resize(self.view.width(), h)

        if self.view.isVisible():
            self.resize(self.width(), h + self.card.height())
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QVariantAnimation, Qt, QAbstractAnimation


class QSmoothlyHoveredPushButton(QPushButton):
    def __init__(self, text='', parent=None, foreground_color=QColor('black'),
                 background_color=QColor('white'), duration=1000):
        super().__init__(text, parent)
        self.setFont(parent.font())
        self.foreground_color = foreground_color
        self.background_color = background_color

        self.animation = QVariantAnimation()
        self.animation.valueChanged.connect(self._on_value_changed)
        self.animation.setStartValue(foreground_color)
        self.animation.setEndValue(background_color)
        self.animation.setDuration(duration)
        self._update_stylesheet(background_color, foreground_color, foreground_color)
        self.setCursor(Qt.PointingHandCursor)

    def _on_value_changed(self, color):
        if self.animation.direction() == QAbstractAnimation.Forward:
            foreground = self.foreground_color
        else:
            foreground = self.background_color
        self._update_stylesheet(color, foreground, self.foreground_color)

    def _update_stylesheet(self, background, foreground, border):
        user_stylesheet = '\n'.join(self.styleSheet().splitlines()[3:])
        super().setStyleSheet(f'background-color: {background.name()} !important;\n'
                              f'color: {foreground.name()} !important;\n'
                              f'border: 2px solid {border.name()} !important;\n'
                              f'padding: 5px 20px;\n' + user_stylesheet)

    def enterEvent(self, event):
        self.animation.setDirection(QAbstractAnimation.Backward)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setDirection(QAbstractAnimation.Forward)
        self.animation.start()
        super().leaveEvent(event)

    def setStyleSheet(self, sheet):
        base_sheet = '\n'.join(self.styleSheet().splitlines()[:3]) + '\n'
        super().setStyleSheet(base_sheet + sheet)

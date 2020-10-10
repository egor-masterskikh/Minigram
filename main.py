# noinspection PyUnresolvedReferences
from PyQt5.uic import loadUi
from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from static.stylesheet import stylesheet
from QSmoothlyHoveredPushButton import QSmoothlyHoveredPushButton
from MyFavouriteColors import COLORS


class MinigramWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.set_font('Ubuntu')
        self.setWindowIcon(QIcon('static/minigram_logo.svg'))

        self.login_btn = QSmoothlyHoveredPushButton(
            'Войти',
            self,
            background_color=QColor('white'),
            foreground_color=QColor(COLORS['Сбербанк']),
            duration=300
        )
        self.login_btn.setStyleSheet('padding: 15px auto; margin-bottom: 30px; margin-top: 30px;')
        self.login_grid.addWidget(self.login_btn, 4, 0)

        self.register_btn = QSmoothlyHoveredPushButton(
            'Зарегистрироваться',
            self,
            background_color=QColor('white'),
            foreground_color=QColor(COLORS['Сбербанк']),
            duration=300
        )
        self.register_btn.setStyleSheet('padding: 15px auto; margin-top: 30px;')
        self.register_grid.addWidget(self.register_btn, 12, 0)

        self.setStyleSheet('* {font-family: "%s";}\n' % self.font().family() + stylesheet)

    def set_font(self, family_name):
        font_db = QFontDatabase()
        font_db.addApplicationFont(
            f'https://fonts.googleapis.com/css2?family={family_name}&display=swap'
        )
        self.setFont(QFont(family_name, 12))


if __name__ == '__main__':
    app = QApplication(argv)
    widget = MinigramWidget()
    widget.showMaximized()
    exit(app.exec())

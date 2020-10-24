from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QWidget, QSizeGrip
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from static.stylesheet import stylesheet
from QSmoothlyHoveredPushButton import QSmoothlyHoveredPushButton
from MyFavouriteColors import COLORS
from ui_main import Ui_MainWindow
from PyQt5.QtCore import Qt, QSize


class MinigramWidget(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_font('Ubuntu')

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.dragPos = None
        self.maximize_btn_side = 10
        self.GLOBAL_STATE = 0
        self.sizegrip = QSizeGrip(self.grip_frame)

        self.maximize_btn.clicked.connect(self.maximize_restore)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)
        self.window_btns.enterEvent = self.show_btn_icons
        self.window_btns.leaveEvent = self.hide_btn_icons
        self.title_bar.mouseMoveEvent = self.moveWindow

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

        self.to_register_page_link.clicked.connect(self.go_to_register_page)
        self.to_login_page_arrow.clicked.connect(self.go_to_login_page)

        self.maximize_restore()

    def moveWindow(self, event):
        if self.GLOBAL_STATE:
            self.maximize_restore()
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.dragPos)
            self.dragPos = event.globalPos()
            event.accept()

    def show_btn_icons(self, *_):
        self.close_btn.setIconSize(QSize(10, 10))
        self.minimize_btn.setIconSize(QSize(10, 10))
        self.maximize_btn.setIconSize(QSize(self.maximize_btn_side, self.maximize_btn_side))

    def hide_btn_icons(self, *_):
        self.close_btn.setIconSize(QSize(0, 0))
        self.minimize_btn.setIconSize(QSize(0, 0))
        self.maximize_btn.setIconSize(QSize(0, 0))

    def mousePressEvent(self, event):
        self.dragPos = event.globalPos()

    def maximize_restore(self):
        if not self.GLOBAL_STATE:
            self.GLOBAL_STATE = 1
            self.maximize_btn.setIcon(QIcon('static/normal.svg'))
            self.maximize_btn_side = 14
            self.showMaximized()
            self.hide_btn_icons()
        else:
            self.GLOBAL_STATE = 0
            self.maximize_btn.setIcon(QIcon('static/maximize.svg'))
            self.maximize_btn_side = 10
            self.showNormal()
            self.hide_btn_icons()

    def go_to_register_page(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)

    def go_to_login_page(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)

    def set_font(self, family_name):
        font_db = QFontDatabase()
        font_db.addApplicationFont(
            f'https://fonts.googleapis.com/css2?family={family_name}&display=swap'
        )
        self.setFont(QFont(family_name, 12))


if __name__ == '__main__':
    app = QApplication(argv)
    MinigramWidget()
    exit(app.exec())

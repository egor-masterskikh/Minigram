# noinspection PyUnresolvedReferences
from PyQt5.uic import loadUi
from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon, QFontDatabase, QFont


class MinigramWidget(QWidget):
    def __init__(self):
        super().__init__()
        loadUi('main.ui', self)
        self.set_font('Ubuntu')
        self.setWindowIcon(QIcon('static/minigram_logo.svg'))

    def set_font(self, family_name):
        font_db = QFontDatabase()
        font_db.addApplicationFont(
            f'https://fonts.googleapis.com/css2?family={family_name}&display=swap'
        )
        self.setFont(QFont(family_name))


if __name__ == '__main__':
    app = QApplication(argv)
    widget = MinigramWidget()
    widget.show()
    exit(app.exec())

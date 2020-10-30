from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QWidget, QSizeGrip
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from static.stylesheet import stylesheet
from QSmoothlyHoveredPushButton import QSmoothlyHoveredPushButton
from MyFavouriteColors import COLORS
from ui_main import Ui_MainWindow
from PyQt5.QtCore import Qt, QSize
import sqlite3
from string import ascii_letters, digits
import hashlib
import os
import binascii


class MainError(Exception):
    pass


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
        self.db = sqlite3.connect('main_db.sqlite')
        self.db_cursor = self.db.cursor()

        self.maximize_btn.clicked.connect(self.maximize_restore)
        self.minimize_btn.clicked.connect(self.showMinimized)
        self.close_btn.clicked.connect(self.close)
        self.window_btns.enterEvent = self.show_btn_icons
        self.window_btns.leaveEvent = self.hide_btn_icons
        self.title_bar.mouseMoveEvent = self.moveWindow

        self.dialog_window_and_message_edit_splitter.setSizes([1000000, 50])
        # 1000000 - рандомное большое число, чтобы указать следующим элементом размер строки
        # сообщения

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
        self.register_btn.clicked.connect(self.register)
        self.register_grid.addWidget(self.register_btn, 15, 0)

        self.register_password_edit.textChanged.connect(self.check_passwords_correctness)
        self.repeat_password_edit.textChanged.connect(self.check_passwords_correctness)

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

    def register(self):
        self.register_email_error_label.clear()
        self.register_nick_error_label.clear()
        all_valid = True

        email = self.register_email_edit.text().strip()
        try:
            self.check_email_correctness(email)
        except MainError as error:
            all_valid = False
            self.register_email_error_label.setText(str(error))

        nick = self.register_nick_edit.text().strip()
        try:
            self.check_nick_correctness(nick)
        except MainError as error:
            all_valid = False
            self.register_nick_error_label.setText(str(error))

        if not self.check_passwords_correctness():
            all_valid = False

        if all_valid:
            password = self.register_password_edit.text().strip()
            password_hash = self.hash_password(password)
            self.db_cursor.execute(
                """
                insert into users(nick, email, password) values(?, ?, ?)
                """, (nick, email, password_hash)
            )
            self.db.commit()
            self.clear_text_from_widgets(
                (self.register_nick_error_label, self.register_nick_edit, self.register_email_edit,
                 self.register_email_error_label, self.register_password_edit,
                 self.repeat_password_edit)
            )
            self.go_to_login_page()

    @staticmethod
    def clear_text_from_widgets(widgets):
        for widget in widgets:
            widget.clear()

    @staticmethod
    def hash_password(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        password_hash = hashlib.pbkdf2_hmac(
            'sha512', password.encode('utf-8'), salt, 100000
        )
        password_hash = binascii.hexlify(password_hash)
        return (salt + password_hash).decode('ascii')

    @staticmethod
    def verify_password(stored_password_hash, provided_password):
        salt = stored_password_hash[:64]
        stored_password = stored_password_hash[64:]
        password_hash = hashlib.pbkdf2_hmac(
            'sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000
        )
        password_hash = binascii.hexlify(password_hash).decode('ascii')
        return password_hash == stored_password

    def check_email_correctness(self, email):
        if not email:
            raise MainError('Напишите свой Email')
        elif set(email) - set(ascii_letters + digits + '@-_.'):
            raise MainError('Мы не приветствуем используемые Вами символы')
        elif '..' in email:
            raise MainError('Кажется, Вы ввели несколько точек подряд')
        elif email.startswith('.') or email.endswith('.'):
            raise MainError('Email не может начинаться с точки или заканчиваться точкой')
        elif email.count('@') != 1:
            raise MainError('Символ "@" должен быть, и только один')
        same_email = self.db_cursor.execute(
            """
            select email from users
            where email = ?
            """, (email,)
        ).fetchone()
        if same_email:
            raise MainError(f'Email "{same_email[0]}" уже занят')

    def check_nick_correctness(self, nick):
        if not nick:
            raise MainError('Придумайте свой ник')
        elif set(nick) - set(ascii_letters + digits + '_'):
            raise MainError('Использованы недопустимые символы')
        elif len(nick) > 30:
            raise MainError('Длина никнейма не должна превышать 30 символов')
        same_nick = self.db_cursor.execute(
            """
            select nick from users
            where nick = ?
            """, (nick,)
        ).fetchone()
        if same_nick:
            raise MainError(f'Ник "{same_nick[0]}" уже занят')

    def check_passwords_correctness(self, *_):
        password1 = self.register_password_edit.text().strip()
        password2 = self.repeat_password_edit.text().strip()

        if len(password1) <= 8:
            self.length_validator.setChecked(False)
            self.digits_letters_validator.setChecked(False)
            self.passwords_match_validator.setChecked(False)
            return False
        else:
            self.length_validator.setChecked(True)

        if not (set(password1).intersection(set(digits)) and set(password1).intersection(
                set(ascii_letters))):
            self.digits_letters_validator.setChecked(False)
            self.passwords_match_validator.setChecked(False)
            return False
        else:
            self.digits_letters_validator.setChecked(True)

        if password1 != password2:
            self.passwords_match_validator.setChecked(False)
            return False
        else:
            self.passwords_match_validator.setChecked(True)
            return True


if __name__ == '__main__':
    app = QApplication(argv)
    MinigramWidget()
    exit(app.exec())

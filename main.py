from sys import exit, argv
from PyQt5.QtWidgets import (QApplication, QWidget, QSizeGrip, QListWidgetItem, QLabel,
                             QHBoxLayout, QSizePolicy, QPlainTextEdit)
from PyQt5.QtGui import QIcon, QFontDatabase, QFont, QColor
from static.stylesheet import stylesheet
from QSmoothlyHoveredPushButton import QSmoothlyHoveredPushButton
from MyFavouriteColors import COLORS
from ui_main import Ui_MainWindow
from PyQt5.QtCore import Qt, QSize, QByteArray, QTimer
import sqlite3
from string import ascii_letters, digits
import hashlib
import os
import binascii
from datetime import datetime, timezone
from zipfile import ZipFile


class MainError(Exception):
    pass


class MinigramWidget(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # ----- Менеджер окна ----- #
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
        # /----- Менеджер окна ----- #

        # ----- База данных ----- #
        self.db = sqlite3.connect('main_db.sqlite')
        self.db_cursor = self.db.cursor()
        # /----- База данных ----- #

        # ----- Обработчики ----- #
        self.to_register_page_link.clicked.connect(self.go_to_register_page)
        self.to_login_page_arrow.clicked.connect(self.go_to_login_page)
        self.send_message_btn.clicked.connect(self.send_message)

        self.email_edit.setFocus()
        self.email_edit.returnPressed.connect(self.login)
        self.password_edit.returnPressed.connect(self.login)
        self.register_email_edit.returnPressed.connect(self.register)
        self.register_nick_edit.returnPressed.connect(self.register)
        self.register_password_edit.returnPressed.connect(self.register)
        self.repeat_password_edit.returnPressed.connect(self.register)

        self.register_password_edit.textChanged.connect(self.check_passwords_correctness)
        self.repeat_password_edit.textChanged.connect(self.check_passwords_correctness)
        self.search.textChanged.connect(self.search_users)
        self.message_edit.textChanged.connect(self.set_send_message_btn_visible)

        self.users_list.itemSelectionChanged.connect(self.display_chat)
        self.message_edit.keyPressEvent = self.message_edit_key_press_event
        # /----- Обработчики ----- #

        # ----- Стили ----- #
        self.set_font('Ubuntu')
        self.setStyleSheet('* {font-family: "%s";}\n' % self.font().family() + stylesheet)
        # /----- Стили ----- #

        # ----- Кнопки входа и регистрации ----- #
        self.login_btn = QSmoothlyHoveredPushButton('Войти', self,
                                                    QColor(COLORS['Сбербанк']),
                                                    QColor('white'), 300)
        self.login_btn.setStyleSheet('padding: 15px auto; margin-bottom: 30px; margin-top: 30px;')
        self.login_btn.clicked.connect(self.login)
        self.login_grid.addWidget(self.login_btn, 6, 0)

        self.register_btn = QSmoothlyHoveredPushButton('Зарегистрироваться', self,
                                                       QColor(COLORS['Сбербанк']),
                                                       QColor('white'), 300)
        self.register_btn.setStyleSheet('padding: 15px auto; margin-top: 30px;')
        self.register_btn.clicked.connect(self.register)
        self.register_grid.addWidget(self.register_btn, 15, 0)
        # /----- Кнопки входа и регистрации ----- #

        self.remember_me_file_path = 'login_data.txt'
        self.current_user_id = None
        # Прижимаю строку ввода к низу
        self.dialog_window_and_message_edit_splitter.setSizes([1_000_000, 0])

        self.chat_timer = QTimer(self)
        self.chat_timer.setInterval(1000)
        self.chat_timer.timeout.connect(lambda: self.display_chat(from_timer=True))
        self.chat_timer.start()

        self.login(from_remember_me_file=True)
        self.maximize_restore()

    # ----- Методы менеджера окна ----- #
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
    # /----- Методы менеджера окна ----- #

    def go_to_register_page(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)
        self.register_email_edit.setFocus()

    def go_to_login_page(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)
        self.email_edit.setFocus()

    def go_to_main_page(self):
        self.stacked_widget.setCurrentWidget(self.main_widget)
        self.display_chatted_users()

    def set_font(self, family_name):
        font_db = QFontDatabase()
        font_db.removeAllApplicationFonts()
        font_archive = ZipFile(f'static/fonts/{family_name}.zip')
        for font_name in font_archive.namelist():
            with font_archive.open(font_name) as font_file:
                font_data = font_file.read()
                font_data_as_bytearray = QByteArray(font_data)
                font_db.addApplicationFontFromData(font_data_as_bytearray)
        family_name = family_name.replace('_', ' ')
        self.setFont(QFont(family_name, 12))

    @staticmethod
    def clear_text_from_widgets(*widgets):
        for widget in widgets:
            widget.clear()

    def can_login(self, email, password):
        found_password_tp = self.db_cursor.execute(
            """
            select password from users
            where email = ?
            """, (email,)
        ).fetchone()

        if not found_password_tp:
            return False
        else:
            found_password, = found_password_tp
            if not self.verify_password(found_password, password):
                return False
            return True

    @staticmethod
    def verify_password(stored_password_hash, provided_password):
        salt = stored_password_hash[:64]
        stored_password = stored_password_hash[64:]
        password_hash = hashlib.pbkdf2_hmac(
            'sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000
        )
        password_hash = binascii.hexlify(password_hash).decode('ascii')
        return password_hash == stored_password

    def login(self, from_remember_me_file=False):
        if from_remember_me_file:
            if os.path.exists(self.remember_me_file_path):
                with open(self.remember_me_file_path) as remember_me_file:
                    login_data = remember_me_file.read().strip().splitlines()
                    if len(login_data) == 2:
                        email, password = login_data
                        if self.can_login(email, password):
                            self.current_user_id = self.get_user_id_by_email(email)
                            self.go_to_main_page()

        else:
            self.login_error_label.clear()
            email = self.email_edit.text().strip()
            password = self.password_edit.text().strip()

            if not self.can_login(email, password):
                self.login_error_label.setText('Неверный email или пароль')
            else:
                with open(self.remember_me_file_path, 'w') as remember_me_file:
                    if self.remember_me_checkbox.isChecked():
                        remember_me_file.write(email + '\n' + password)

                self.clear_text_from_widgets(
                    self.email_edit, self.password_edit, self.login_error_label
                )
                self.current_user_id = self.get_user_id_by_email(email)
                self.go_to_main_page()

    @staticmethod
    def hash_password(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        password_hash = hashlib.pbkdf2_hmac(
            'sha512', password.encode('utf-8'), salt, 100000
        )
        password_hash = binascii.hexlify(password_hash)
        return (salt + password_hash).decode('ascii')

    def check_email_correctness(self, email):
        if not email:
            raise MainError('Напишите свой Email')
        elif set(email) - set(ascii_letters + digits + '@-_.'):
            raise MainError('Мы не приветствуем используемые Вами символы')
        elif '..' in email:
            raise MainError('Кажется, Вы ввели несколько точек подряд')
        elif email.startswith('.') or email.endswith('.'):
            raise MainError('Email не может начинаться с точки или заканчиваться точкой')
        elif not email.count('@'):
            raise MainError('Нет символа "@"')
        elif email.count('@') > 1:
            raise MainError('Символ "@" должен быть только один')
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
                self.register_nick_error_label, self.register_nick_edit, self.register_email_edit,
                self.register_email_error_label, self.register_password_edit,
                self.repeat_password_edit
            )
            self.current_user_id = self.get_user_id_by_email(email)
            self.go_to_main_page()

    def get_user_id_by_email(self, email):
        user_id_tp = self.db_cursor.execute(
            """
            select id from users
            where email = ?
            """, (email,)
        ).fetchone()
        if not user_id_tp:
            return
        else:
            return user_id_tp[0]

    def display_users(self, nicks: list, selected_nick=None):
        self.users_list.clear()
        self.dialog_window.clear()
        self.message_widget.setVisible(False)
        self.user_info_widget.setVisible(False)
        if selected_nick:
            for nick in nicks:
                chat_item = QListWidgetItem(nick)
                chat_item.setTextAlignment(Qt.AlignCenter)
                self.users_list.addItem(chat_item)
                if nick == selected_nick:
                    self.users_list.setCurrentItem(chat_item)
                    self.display_chat()
        else:
            for nick in nicks:
                chat_item = QListWidgetItem(nick)
                chat_item.setTextAlignment(Qt.AlignCenter)
                self.users_list.addItem(chat_item)

    def display_chatted_users(self, selected_nick=None):
        nicks = [nick for nick, in self.db_cursor.execute(
            """
            select nick from users
            where id in (
                select recipient_id from messages
                where sender_id = ?
            ) or id in (
                select sender_id from messages
                where recipient_id = ?
            ) order by nick
            """, (self.current_user_id, self.current_user_id)
        ).fetchall()]

        if selected_nick and selected_nick not in nicks:
            nicks.append(selected_nick)
            nicks.sort()

        self.display_users(nicks, selected_nick)

    def display_chat(self, with_users_update=False, from_timer=False):
        selected_user = self.users_list.currentItem()
        if not selected_user:
            if with_users_update:
                self.display_chatted_users()
            return

        selected_nick = selected_user.text()
        if with_users_update:
            self.users_list.itemSelectionChanged.disconnect()
            self.display_chatted_users(selected_nick)
            self.search.clear()
            self.users_list.itemSelectionChanged.connect(self.display_chat)

        if not from_timer:
            self.message_edit.clear()

        self.dialog_window.clear()
        self.message_widget.setVisible(True)
        self.user_info_widget.setVisible(True)
        self.set_send_message_btn_visible()
        self.nick.setText(selected_nick)
        if not self.search.hasFocus():
            self.message_edit.setFocus()

        sent_messages = self.db_cursor.execute(
            """
            select body, timestamp from messages
            where sender_id = ? and recipient_id = (
                select id from users
                where nick = ?
            )
            """, (self.current_user_id, selected_nick)
        ).fetchall()
        received_messages = self.db_cursor.execute(
            """
            select body, timestamp from messages
            where recipient_id = ? and sender_id = (
                select id from users
                where nick = ?
            )
            """, (self.current_user_id, selected_nick)
        ).fetchall()

        def get_local_datetime(datetime_str):
            return datetime.fromisoformat(datetime_str).replace(tzinfo=timezone.utc).astimezone(
                tz=None)

        messages = sorted(
            map(lambda message: (message[0], get_local_datetime(message[1]), message[2]), (
                *map(lambda message: (*message, 'sent'), sent_messages),
                *map(lambda message: (*message, 'received'), received_messages)
            )), key=lambda message: message[1]
        )

        for body, timestamp, mode in messages:
            message_row_widget = QWidget()
            message_row_widget_hbox = QHBoxLayout(message_row_widget)

            message_widget = QWidget()
            message_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            message_widget.setStyleSheet('font-size: 12pt; border-radius: 10px;')
            message_widget_hbox = QHBoxLayout(message_widget)

            message_body_label = QLabel(body)
            message_body_label.setWordWrap(True)

            message_timestamp_label = QLabel(timestamp.strftime('%H:%M'))
            message_timestamp_label.setStyleSheet(f'color: {COLORS["Асфальт"]}; margin-top: 10px;')

            message_widget_hbox.addWidget(message_body_label)
            message_widget_hbox.addWidget(message_timestamp_label)

            margin = QWidget()
            margin.setMinimumWidth(30)

            if mode == 'sent':
                message_row_widget_hbox.addWidget(margin)
                message_row_widget_hbox.addWidget(message_widget)
                message_widget.setStyleSheet(
                    message_widget.styleSheet() + f'background-color: {COLORS["Бело-зелёный"]}'
                )
            else:
                message_row_widget_hbox.addWidget(message_widget)
                message_row_widget_hbox.addWidget(margin)
                message_widget.setStyleSheet(
                    message_widget.styleSheet() + 'background-color: white;'
                )

            message_item = QListWidgetItem()
            message_item.setFlags(Qt.ItemIsEnabled)
            message_item.setSizeHint(message_row_widget.sizeHint())
            self.dialog_window.addItem(message_item)
            self.dialog_window.setItemWidget(message_item, message_row_widget)

    def send_message(self):
        body = self.message_edit.toPlainText().strip()
        if not body:
            return
        recipient_id, = self.db_cursor.execute(
            """
            select id from users
            where nick = ?
            """, (self.nick.text(),)
        ).fetchone()

        self.db_cursor.execute(
            """
            insert into messages(body, recipient_id, sender_id) values(?, ?, ?)
            """, (body, recipient_id, self.current_user_id)
        )
        self.db.commit()

        self.display_chat()

    def set_send_message_btn_visible(self):
        text = self.message_edit.toPlainText().strip()
        self.send_message_btn.setVisible(bool(text))

    def message_edit_key_press_event(self, event):
        if int(event.modifiers()) == Qt.ControlModifier:
            if event.key() == Qt.Key_Return:
                self.send_message()
                return
        QPlainTextEdit.keyPressEvent(self.message_edit, event)

    def search_users(self):
        entered_nick = self.search.text().strip()
        selected_user = self.users_list.currentItem()
        if selected_user:
            selected_nick = selected_user.text()
        else:
            selected_nick = None

        if not entered_nick:
            self.display_chatted_users(selected_nick=selected_nick)
        else:
            found_nicks = [nick for nick, in self.db_cursor.execute(
                """
                select nick from users
                where nick like ? and nick != (
                    select nick from users
                    where id = ?
                ) order by nick
                """, (f'%{entered_nick}%', self.current_user_id)
            ).fetchall()]

            self.users_list.itemSelectionChanged.disconnect()

            self.display_users(found_nicks, selected_nick=selected_nick)

            self.users_list.itemSelectionChanged.connect(
                lambda: self.display_chat(with_users_update=True)
            )

            self.search.setFocus()


if __name__ == '__main__':
    app = QApplication(argv)
    MinigramWidget()
    exit(app.exec())

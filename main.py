from sys import exit, argv
from PyQt5.QtWidgets import QApplication, QWidget, QSizeGrip, QListWidgetItem, QLabel, \
    QHBoxLayout, QSizePolicy, QPlainTextEdit
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
from datetime import datetime, timezone
from zipfile import ZipFile
from PyQt5.QtCore import QByteArray


class MainError(Exception):
    pass


class MinigramWidget(QWidget, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_font('Ubuntu')

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.current_user_email = None
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

        self.dialog_window_and_message_edit_splitter.setSizes([1_000_000, 0])
        # 1000000 - рандомное большое число, чтобы максимально прижать строку ввода к низу

        self.login_btn = QSmoothlyHoveredPushButton(
            'Войти',
            self,
            background_color=QColor('white'),
            foreground_color=QColor(COLORS['Сбербанк']),
            duration=300
        )
        self.login_btn.setStyleSheet('padding: 15px auto; margin-bottom: 30px; margin-top: 30px;')
        self.login_btn.clicked.connect(self.login)
        self.login_grid.addWidget(self.login_btn, 6, 0)

        self.email_edit.returnPressed.connect(self.login)
        self.email_edit.setFocus()
        self.password_edit.returnPressed.connect(self.login)

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

        self.register_email_edit.returnPressed.connect(self.register)
        self.register_nick_edit.returnPressed.connect(self.register)
        self.register_password_edit.returnPressed.connect(self.register)
        self.repeat_password_edit.returnPressed.connect(self.register)

        self.register_password_edit.textChanged.connect(self.check_passwords_correctness)
        self.repeat_password_edit.textChanged.connect(self.check_passwords_correctness)

        self.users_list.itemSelectionChanged.connect(self.display_chat)
        self.message_edit.textChanged.connect(self.set_send_message_btn_visible)

        self.send_message_btn.clicked.connect(self.send_message)
        self.message_edit.keyPressEvent = self.message_edit_key_press_event

        self.search.textChanged.connect(self.search_users)

        self.setStyleSheet('* {font-family: "%s";}\n' % self.font().family() + stylesheet)

        self.to_register_page_link.clicked.connect(self.go_to_register_page)
        self.to_login_page_arrow.clicked.connect(self.go_to_login_page)

        self.login_data_filepath = 'login_data.txt'
        if os.path.exists(self.login_data_filepath):
            with open(self.login_data_filepath) as login_data_file:
                login_data = login_data_file.read().strip().splitlines()
                if len(login_data) == 2:
                    email, password_hash = login_data
                    user_id = self.db_cursor.execute(
                        """
                        select id from users
                        where email = ? and password = ?
                        """, (email, password_hash)
                    ).fetchone()
                    if user_id:
                        self.current_user_email = email
                        self.go_to_main_page()

        self.maximize_restore()

    def set_send_message_btn_visible(self):
        text = self.message_edit.toPlainText().strip()
        self.send_message_btn.setVisible(bool(text))

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

    def login(self):
        self.login_error_label.clear()
        email = self.email_edit.text().strip()

        found_password_tp = self.db_cursor.execute(
            """
            select password from users
            where email = ?
            """, (email,)
        ).fetchone()
        if not found_password_tp:
            self.login_error_label.setText('Неверный логин или пароль')
            return

        entered_password = self.password_edit.text().strip()
        found_password = found_password_tp[0]

        if not self.verify_password(found_password, entered_password):
            self.login_error_label.setText('Неверный логин или пароль')
            return

        with open(self.login_data_filepath, 'w') as login_data_file:
            if self.remember_me_checkbox.isChecked():
                login_data_file.write(email + '\n' + found_password)

        self.clear_text_from_widgets(
            (self.email_edit, self.password_edit, self.login_error_label)
        )
        self.current_user_email = email
        self.go_to_main_page()

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

            self.current_user_email = email
            self.go_to_main_page()

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
                where sender_id in (
                    select id from users
                    where email = ?
                )
            ) or id in (
                select sender_id from messages
                where recipient_id in (
                    select id from users
                    where email = ?
                )
            ) order by nick
            """, (self.current_user_email, self.current_user_email)
        ).fetchall()]

        if selected_nick and selected_nick not in nicks:
            nicks.append(selected_nick)
            nicks.sort()

        self.display_users(nicks, selected_nick)

    def display_chat(self, with_users_update=False):
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

        self.message_edit.clear()
        self.dialog_window.clear()
        self.message_widget.setVisible(True)
        self.user_info_widget.setVisible(True)
        self.set_send_message_btn_visible()
        self.nick.setText(selected_nick)
        self.message_edit.setFocus()

        sent_messages = self.db_cursor.execute(
            """
            select body, timestamp from messages
            where sender_id = (
                select id from users
                where email = ?
            ) and recipient_id = (
                select id from users
                where nick = ?
            )
            """, (self.current_user_email, selected_nick)
        ).fetchall()
        received_messages = self.db_cursor.execute(
            """
            select body, timestamp from messages
            where recipient_id = (
                select id from users
                where email = ?
            ) and sender_id = (
                select id from users
                where nick = ?
            )
            """, (self.current_user_email, selected_nick)
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
            message_body_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
            message_body_label.setCursor(Qt.IBeamCursor)

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
        sender_id, = self.db_cursor.execute(
            """
            select id from users
            where email = ?
            """, (self.current_user_email,)
        ).fetchone()

        self.db_cursor.execute(
            """
            insert into messages(body, recipient_id, sender_id) values(?, ?, ?)
            """, (body, recipient_id, sender_id)
        )
        self.db.commit()

        self.message_edit.clear()
        # self.show_chat()

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
                    where email = ?
                ) order by nick
                """, (f'%{entered_nick}%', self.current_user_email)
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

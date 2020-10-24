from MyFavouriteColors import COLORS


stylesheet = """
#CustomWindow {
    background-color: white;
    border-radius: 10px;
}

#delimiter {
    background-color: %s;
}

#title {
    padding-right: 92px;
    color: %s;
}

#login_widget QLineEdit, #register_widget QLineEdit {
    selection-background-color: %s;
    selection-color: white;
    border-width: 2px;
    border-style: solid;
    border-top: 0;
    border-left: 0;
    border-right: 0;
    border-color: black;
}

#login_widget QLineEdit:focus, #register_widget QLineEdit:focus {
    border-color: %s;
}

QCommandLinkButton {
    background: none;
    border: none;
    font-weight: normal;
    color: %s;
}

#valid_symbols_label {
    color: %s;
    margin-bottom: 10px;
}

#register_widget QCheckBox:unchecked {
    color: %s;
}

#register_widget QCheckBox:checked {
    color: %s;
}

#register_widget QCheckBox::indicator {
    border: none;
}

#length_validator {
    margin-top: 20px;
}
""" % (COLORS['Сбербанк'], COLORS['Сбербанк'], COLORS['Сбербанк'], COLORS['Сбербанк'],
       COLORS['Кобальт синий'], COLORS['Текст на песочном'], COLORS['Карминово-красный'],
       COLORS['Сбербанк'])

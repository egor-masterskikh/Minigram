--
-- Файл сгенерирован с помощью SQLiteStudio v3.2.1 в Пт окт 30 09:34:53 2020
--
-- Использованная кодировка текста: UTF-8
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Таблица: messages
CREATE TABLE messages (
    id           INTEGER  PRIMARY KEY ON CONFLICT FAIL AUTOINCREMENT
                          UNIQUE ON CONFLICT FAIL
                          NOT NULL ON CONFLICT FAIL,
    body         TEXT     NOT NULL ON CONFLICT FAIL,
    sender_id    INTEGER  REFERENCES users (id) ON DELETE SET NULL
                          UNIQUE ON CONFLICT FAIL,
    recipient_id INTEGER  REFERENCES users (id) ON DELETE SET NULL
                          UNIQUE ON CONFLICT FAIL,
    timestamp    DATETIME NOT NULL
);


-- Таблица: users
CREATE TABLE users (
    id       INTEGER      PRIMARY KEY ON CONFLICT FAIL AUTOINCREMENT
                          UNIQUE ON CONFLICT FAIL
                          NOT NULL ON CONFLICT FAIL,
    nick     VARCHAR (30) UNIQUE ON CONFLICT FAIL
                          NOT NULL ON CONFLICT FAIL,
    email    TEXT         UNIQUE ON CONFLICT FAIL
                          NOT NULL ON CONFLICT FAIL,
    password TEXT         NOT NULL ON CONFLICT FAIL
);


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;

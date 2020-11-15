DROP TABLE IF EXISTS messages;
CREATE TABLE messages (
    id           INTEGER  PRIMARY KEY ON CONFLICT FAIL AUTOINCREMENT
                          UNIQUE ON CONFLICT FAIL
                          NOT NULL ON CONFLICT FAIL,
    body         TEXT     NOT NULL ON CONFLICT FAIL,
    sender_id    INTEGER  REFERENCES users (id) ON DELETE SET NULL,
    recipient_id INTEGER  REFERENCES users (id) ON DELETE SET NULL,
    timestamp    DATETIME NOT NULL ON CONFLICT FAIL
                          DEFAULT (CURRENT_TIMESTAMP) 
);

DROP TABLE IF EXISTS users;
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

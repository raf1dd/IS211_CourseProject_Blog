DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    content TEXT NOT NULL,
    published_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_published INTEGER NOT NULL DEFAULT 1 CHECK (is_published IN (0, 1))
);

INSERT INTO users (username, password) VALUES ('admin', 'password');

INSERT INTO posts (title, author, content, published_at, is_published)
VALUES (
    'Welcome to My Flask Blog',
    'admin',
    '<p>This is the first post in my <strong>IS 211</strong> blogging application built with Flask and SQLite.</p>',
    '2026-11-21 03:00:00',
    1
);

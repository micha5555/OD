from flask import flash
import sqlite3

def create_tables(db_name):
    db = sqlite3.connect(db_name)
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            login string NOT NULL PRIMARY KEY,
            password string NOT NULL
            )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NOTES (
            id integer PRIMARY KEY AUTOINCREMENT,
            owner string,
            isPublic boolean,
            isEncrypted booolean,
            content string,
            FOREIGN KEY (owner)
                REFERENCES USERS(login))
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SHAREDNOTES (
            noteId integer,
            user string,
            FOREIGN KEY (noteId)
                REFERENCES NOTES(id),
            FOREIGN KEY (user)
                REFERENCES USERS(login))
    ''')
    db.commit()
    db.close()

def register_user(login, password):
    db = sqlite3.connect("database.db")
    cursor = db.cursor()
    cursor.execute("SELECT login FROM USERS WHERE login IN (?)", (login,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        cursor.execute("INSERT INTO USERS (login, password) VALUES (?, ?)", (login, password))
        db.commit()
        flash("Zarejestrowano pomyslnie")
    else:
        flash("Login " + login + " jest zajęty")
    db.close()
from flask import flash
import sqlite3

DBNAME = "database.db"

def create_tables():
    db = sqlite3.connect(DBNAME)
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS (
            login string NOT NULL PRIMARY KEY,
            password string NOT NULL,
            salt string NOT NULL
            )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NOTES (
            id integer PRIMARY KEY AUTOINCREMENT,
            owner string,
            isPublic boolean,
            isEncrypted booolean,
            content string,
            salt string NOT NULL,
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

def register_user(login, password, salt):
    db = sqlite3.connect(DBNAME)
    cursor = db.cursor()
    cursor.execute("SELECT login FROM USERS WHERE login IN (?)", (login,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        cursor.execute("INSERT INTO USERS (login, password, salt) VALUES (?, ?, ?)", (login, password, salt))
        db.commit()
        flash("Zarejestrowano pomyslnie")
    else:
        flash("Login " + login + " jest zajęty")
    db.close()

def get_credentials_by_login(login):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT login, password FROM users WHERE login == (?)", (login,))
    userRow = sql.fetchone()
    db.close()
    return userRow

def get_user_salt(login):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT salt FROM users WHERE login == (?)", (login,))
    salt = sql.fetchone()[0]
    db.close()
    return salt

def get_ids_of_user_notes(login):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT id FROM NOTES WHERE owner == (?)", (login,))
    notesIds = sql.fetchall()
    db.close()
    return notesIds

def get_public_notes():
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT id, owner, content FROM NOTES WHERE isPublic = 1")
    publicNotes= sql.fetchall()
    db.close()
    return publicNotes

def get_notes_shared_to_user(login):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(F"SELECT NOTES.id, NOTES.owner, NOTES.content FROM SHAREDNOTES INNER JOIN NOTES ON SHAREDNOTES.noteId=NOTES.id WHERE SHAREDNOTES.user == (?)", (login,))
    sharedToUserNotes = sql.fetchall()
    db.close()
    return sharedToUserNotes

def add_new_note(login, note, salt, isEncrypted, isPublic):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"INSERT INTO NOTES (owner, content, salt, isEncrypted, isPublic) VALUES (?, ?, ?, ?, ?)", (login, note, salt, isEncrypted, isPublic))
    db.commit()
    db.close()

def get_note_with_id(noteId):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT id, owner, content, salt, isPublic, isEncrypted FROM notes WHERE id = (?)", (noteId,))
    note = sql.fetchone()
    db.close()
    return note

def get_users_having_access_to_shared_note(noteId):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT user FROM SHAREDNOTES WHERE noteId = (?)", (noteId,))
    usersWithAccess = sql.fetchall()
    db.close()
    tmp = ()
    for elem in usersWithAccess:
        tmp = tmp + elem
    return tmp

def check_if_user_exists(login):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"SELECT login FROM USERS WHERE login = (?)", (login,))
    userLogin = sql.fetchone()
    db.close()
    if userLogin == None or len(userLogin) == 0:
        return False
    return True

def share_note_with_user(userLogin, id):
    db = sqlite3.connect(DBNAME)
    sql = db.cursor()
    sql.execute(f"INSERT INTO SHAREDNOTES (noteId, user) VALUES (?, ?)", (id, userLogin))
    db.commit()
    db.close()
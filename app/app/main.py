# Notatki można zapisywać be polskich znaków
# Niestety nie udało mi się wrzucić rozwiązania do dockera, uruchomienie: python3 main.py, apliakcja jest dostępna na porcie 5000 na localhoscie

from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import markdown
import bleach
import sqlite3
from argon2 import PasswordHasher
import time

from db_operations import *
from validator import *
from notes_encryptor import *

app = Flask(__name__)

actual_user = ""

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = "854658yuthjtureyu89tjh89trj8h548h754y7854hty8er8ygw875g6854yt88"

DATABASE = "./database.db"

ph = PasswordHasher()

invalidLoginsCounter = 0
mustWait = 0
create_tables(DATABASE)

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username is None:
        return None

    db = sqlite3.connect(DATABASE)
    sql = db.cursor()
    sql.execute(f"SELECT login, password FROM USERS WHERE login IN(?)", (username,))
    row = sql.fetchone()
    try:
        username, password = row
    except:
        return None

    user = User()
    user.id = username
    user.password = password
    return user

@app.route("/", methods=["GET","POST"])
def login():
    global invalidLoginsCounter
    global mustWait
    if mustWait == 1:
        time.sleep(30)
        mustWait = 0

    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        time.sleep(3)
        user = user_loader(username)
        if user is None:
            invalidLoginsCounter = invalidLoginsCounter + 1
            flash("Nieprawidłowy login lub hasło")
            if invalidLoginsCounter == 5:
                flash("Nastąpiło zbyt wiele nieudanych prób logowania, musiałeś chwilę zaczekać")
                mustWait = 1
                invalidLoginsCounter = 0
            return redirect("/")

        try:
            ph.verify(user.password, password)
            login_user(user)
            invalidLoginsCounter = 0
            return redirect('/mainpanel')
        except:
            invalidLoginsCounter = invalidLoginsCounter + 1
            flash("Nieprawidłowy login lub hasło")
            if invalidLoginsCounter == 5:
                flash("Nastąpiło zbyt wiele nieudanych prób logowania, musiałeś chwilę zaczekać")
                mustWait = 1
                invalidLoginsCounter = 0
            return redirect("/")

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")

@app.route("/register", methods=['POST'])
def register():
    if(validate_register_data_corectness(request.form.get("username"), request.form.get("password"), request.form.get("repeated_password"))):
        passwd = ph.hash(request.form.get("password"))
        register_user(request.form.get("username"), passwd)
        return redirect("/")
    else:
        if "submit" in request.form :
            flash("Niepoprawne dane")
        return render_template("registerpanel.html")

@app.route("/mainpanel", methods=['GET', 'POST'])
@login_required
def mainpanel():
    username = current_user.id
    db = sqlite3.connect(DATABASE)
    sql = db.cursor()
    sql.execute(f"SELECT id FROM NOTES WHERE owner == '{username}'")
    notes = sql.fetchall()
    sql.execute(f"SELECT id, owner, content FROM NOTES WHERE isPublic = 1")
    publicNotes= sql.fetchall()
    sql.execute(f"SELECT noteId FROM SHAREDNOTES WHERE user = '{current_user.id}'")
    sharedToMeIds = sql.fetchall()
    idsString = "("
    for elem in sharedToMeIds:
        idsString = idsString + str(elem[0]) + ","
    if len(idsString) > 1:
        idsString = idsString[:len(idsString)-1]
    idsString = idsString + ")"
    sql.execute(f"SELECT id, owner, content FROM NOTES WHERE id IN {idsString}")
    sharedToMeNotes = sql.fetchall()
    

    if request.method == 'GET':
        return render_template("mainpanel.html", username=username, notes=notes, publicNotes=publicNotes, sharedToMeNotes=sharedToMeNotes)
    elif request.method == 'POST':
        isPublic = False
        if request.form.get("isPublic"):
            isPublic = True
        isEncrypted = False
        if request.form.get("isEncrypted"):
            isEncrypted = True
        newNote = request.form.get("newNote","")
        
        if len(newNote) == 0:
            flash("Nie można zapisać pustej notatki")
            return redirect("/mainpanel")
        if isPublic and isEncrypted:
            flash("Nie zapisono notatki, powód: Publiczna notatka nie może być zaszyfrowana!")
            return redirect("/mainpanel")
        if isEncrypted:
            notePassword = request.form.get("notePassword")
            if len(notePassword) == 0:
                flash("Hasło do notatki nie może być puste")
                return redirect("/mainpanel")

            newNoteBytes = bytes(newNote, encoding='utf-8')
            notePasswordBytes = bytes(notePassword, encoding='utf-8')
            encryptedNote = encrypt(notePasswordBytes, newNoteBytes)

            sql.execute(f"INSERT INTO NOTES (owner, content, isEncrypted, isPublic) VALUES (?, ?, ?, ?)", (username, encryptedNote, isEncrypted, isPublic))
            db.commit()
            newNote = ""
            flash("Zapisano zaszyfrowaną notatkę")
            return redirect("/mainpanel")
        db = sqlite3.connect(DATABASE)
        sql = db.cursor()
        sql.execute(f"INSERT INTO NOTES (owner, content, isEncrypted, isPublic) VALUES (?, ?, ?, ?)", (username, newNote, False, isPublic))
        db.commit()
        newNote = ""
        if isPublic:
            flash("Zapisano publiczną notatkę")
        else:
            flash("Zapisano notatkę")
        return redirect("/mainpanel")

@app.route("/mainpanel/<id>", methods=['GET', 'POST'])
@login_required
def render_old(id):
    db = sqlite3.connect(DATABASE)
    sql = db.cursor()
    sql.execute(f"SELECT id, owner, content, isPublic, isEncrypted FROM notes WHERE id = {id}")
    id, owner, content, isPublic, isEncrypted = sql.fetchone()
    if owner != current_user.id:
        isOwner = 0
    else:
        isOwner = 1
    if request.method == 'GET':
        if isOwner == 1 or isPublic == 1:
            rendered = markdown.markdown(content)
            if "<script>" in rendered:
                rendered = bleach.clean(rendered)
            return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note=rendered, isOwner=isOwner)

        sql.execute(f"SELECT user FROM SHAREDNOTES WHERE noteId = '{id}'")
        usersWithAccess = sql.fetchall()
        tmp = ()
        for elem in usersWithAccess:
            tmp = tmp + elem
        if len(tmp) == 0:
            return "Access to note forbidden", 403

        usersWithAccessSingleTuple = tmp[0]
        if not (current_user.id in usersWithAccessSingleTuple):
            return "Access to note forbidden", 403
        rendered = markdown.markdown(content)
        if "<script>" in rendered:
            rendered = bleach.clean(rendered)
        return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note=rendered, isOwner=isOwner)
    elif request.method == 'POST':
        isShare = request.form.get("isShare")
        if(isShare == "true"):
            shareUser = request.form.get("shareUser")
            if(shareUser == current_user.id):
                flash("Nie możesz udostępnić notatki samemu sobie")
                return redirect(str(id))
            sql.execute(f"SELECT login FROM USERS WHERE login = '{shareUser}'")
            userLogin = sql.fetchone()
            if(userLogin == None):
                flash("Użytkownik " + shareUser + " nie istnieje")
                return redirect(str(id))
            
            sql.execute(f"INSERT INTO SHAREDNOTES (noteId, user) VALUES (?, ?)", (id, shareUser))
            db.commit()
            flash("Udostępniono notatkę użytkownikowi " + shareUser)
            return redirect(str(id))
        else:
            notePassword = bytes(request.form.get("notePassword"), encoding='utf-8')
            try:
                decrypted = decrypt(notePassword, content, decode=True)
                decrypted = decrypted.decode("utf-8")
                rendered = markdown.markdown(decrypted)
                if "<script>" in rendered:
                    rendered = bleach.clean(rendered)
                return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note=rendered)
            except:
                flash("Hasło do notatki nieprawidłowe")
                return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note="")

if __name__ == "__main__":
    app.run("0.0.0.0", 5000)
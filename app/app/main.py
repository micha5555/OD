# Notatki można zapisywać be polskich znaków
# Niestety nie udało mi się wrzucić rozwiązania do dockera, uruchomienie: python3 main.py, apliakcja jest dostępna na porcie 5000 na localhoscie

from flask import Flask, render_template, request, redirect, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import markdown
import bleach
from argon2 import PasswordHasher
import time
import secrets

from db_operations import *
from validator import *
from notes_encryptor import *
from common_operations import *

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.secret_key = "854658yuthjtureyu89tjh89trj8h548h754y7854hty8er8ygw875g6854yt88"
pepper = 'F$NPx3V*9`zo)Ec$8Q)~*9tY#jw#Nm#A3Mx1bpWYwwdL4h@iEKYvGEXqKcWY)37j'
ph = PasswordHasher(time_cost = 200)

invalidLoginsCounter = 0
mustWait = 0
create_tables()

class User(UserMixin):
    pass

@login_manager.user_loader
def user_loader(username):
    if username is None:
        return None

    userRow = get_credentials_by_login(username)
    try:
        username, password = userRow
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
        login = request.form.get("username")
        password = request.form.get("password")
        time.sleep(3)

        user = user_loader(login)
        if user is None or not validate_login_and_password(login, password):
            invalidLoginsCounter = invalidLoginsCounter + 1
            flash("Nieprawidłowy login lub hasło")
            if invalidLoginsCounter == 5:
                flash("Nastąpiło zbyt wiele nieudanych prób logowania, musiałeś chwilę zaczekać")
                mustWait = 1
                invalidLoginsCounter = 0
            return redirect("/")

        try:
            salt = get_user_salt(login)
            ph.verify(user.password, salt+password+pepper)
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
    login = request.form.get("username")
    password = request.form.get("password")
    repeatedPassword = request.form.get("repeated_password")
    if validate_register_data(login, password, repeatedPassword):
        salt = secrets.token_urlsafe(16)
        hashedPassword = ph.hash(salt+password+pepper)
        register_user(login, hashedPassword, salt)
        return redirect("/")
    else:
        if "submit" in request.form :
            flash("Niepoprawne dane")
        return render_template("registerpanel.html")

@app.route("/mainpanel", methods=['GET', 'POST'])
@login_required
def mainpanel():
    username = current_user.id
    notes = get_ids_of_user_notes(username)
    publicNotes = get_public_notes()
    sharedNotesToUser = get_notes_shared_to_user(username)
    
    if request.method == 'GET':
        return render_template("mainpanel.html", username=username, notes=notes, publicNotes=publicNotes, sharedToMeNotes=sharedNotesToUser)
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

            add_new_note(username, encryptedNote, isEncrypted, isPublic)
            newNote = ""
            flash("Zapisano zaszyfrowaną notatkę")
            return redirect("/mainpanel")
        add_new_note(username, newNote, False, isPublic)
        newNote = ""
        if isPublic:
            flash("Zapisano publiczną notatkę")
        else:
            flash("Zapisano notatkę")
        return redirect("/mainpanel")

@app.route("/mainpanel/<id>", methods=['GET', 'POST'])
@login_required
def render_old(id):
    note = get_note_with_id(id)
    if note == None:
        flash("Nie można znaleźć notatki")
        return redirect("/mainpanel")
    id, owner, content, isPublic, isEncrypted = note
    isOwner = check_if_owner(owner, current_user.id)
    if request.method == 'GET':
        # to do poprawy
        if isOwner == 1 or isPublic == 1:
            rendered = markdown.markdown(content)
            # if "<script>" in rendered:
            #     rendered = bleach.clean(rendered)
            rendered = bleach.clean(rendered)
            return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note=rendered, isOwner=isOwner)

        usersWithAccess = get_users_having_access_to_shared_note(id)
        if len(usersWithAccess) == 0:
            return "Access to note forbidden", 403

        usersWithAccessSingleTuple = usersWithAccess[0]
        if not (current_user.id in usersWithAccessSingleTuple):
            return "Access to note forbidden", 403
        rendered = markdown.markdown(content)
        # if "<script>" in rendered:
        #     rendered = bleach.clean(rendered)
        return render_template("note.html", id=id, owner=owner, isPublic=isPublic, isEncrypted=isEncrypted, note=rendered, isOwner=isOwner)
    elif request.method == 'POST':
        isShare = request.form.get("isShare")
        if(isShare == "true"):
            shareUser = request.form.get("shareUser")
            if(shareUser == current_user.id):
                flash("Nie możesz udostępnić notatki samemu sobie")
                return redirect(str(id))
            
            if check_if_user_exists(shareUser) == False:
                flash("Użytkownik " + shareUser + " nie istnieje")
                return redirect(str(id))
            
            share_note_with_user(shareUser, id)
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
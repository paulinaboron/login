from flask import Flask, render_template, request, redirect, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired
import sqlite3
from werkzeug.datastructures import MultiDict
import bootstrap4

app = Flask(__name__)
botstrap = Bootstrap(app)
app.config["SECRET_KEY"] = "Qwerty12345!?"

log = ""
pas = ""
userId = 1


class LoginForm(FlaskForm):
    login = StringField("Login", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("OK")


@app.route("/")
def index():
    form = LoginForm()
    return render_template("index.html", form=form, title="Login")


@app.route("/register")
def register():
    form = LoginForm()
    return render_template("register.html", form=form, title="Register")


@app.route("/saveDataRegister", methods=["POST", "GET"])
def saveDataRegister():
    global log
    global pas
    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myCursor.execute(
        """CREATE TABLE if not exists users (
        login text,
        password text
    )"""
    )

    login = request.form["login"]
    password = request.form["password"]
    myCursor.execute("SELECT login FROM users")
    logins = myCursor.fetchall()
    b = 0
    for i in logins:
        print(i[0])
        if login == i[0]:
            b = 1

    if b == 1:
        flash("Login already exists")
        form = LoginForm()
        return render_template("register.html", form=form, title="Register")

    myCursor.execute(
        "INSERT INTO users VALUES (:login, :password)",
        {"login": login, "password": password},
    )
    flash("Konto utworzone")
    myConnection.commit()
    myCursor.execute("SELECT *, oid FROM users")
    records = myCursor.fetchall()
    print(records)
    myConnection.close()
    log = login
    pas = password

    return render_template("saveData.html", title="Konto utworzone", records=records)


@app.route("/saveDataLogin", methods=["POST", "GET"])
def saveDataLogin():
    global log
    global pas
    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myConnection.commit()

    login = request.form["login"]
    password = request.form["password"]

    if login == "admin" and password == "admin":
        log = login
        pas = password
        myCursor.execute("SELECT *, oid FROM users")
        records = myCursor.fetchall()
        return render_template("adminHome.html", title="Home Admin", records=records)

    myCursor.execute("SELECT password FROM users where login='" + login + "'")
    records = myCursor.fetchall()
    print(records, "log")
    myConnection.close()
    if not records:
        flash("Wrong login")
        form = LoginForm()
        return render_template("index.html", form=form, title="Login")

    if records[0][0] == password:
        flash("Zalogowano")
        log = login
        pas = password
        return render_template("saveData.html", title="Zalogowano", records=records)
    else:
        flash("Wrong password")
        form = LoginForm()
        return render_template("index.html", form=form, title="Login")


@app.route("/edit")
def edit():
    global log
    global pas
    form = LoginForm(formdata=MultiDict({"login": log, "password": pas}))
    return render_template(
        "edit.html", title="Edytowanie", form=form, login=log, password=pas
    )


@app.route("/editAdmin")
def editAdmin():
    global log
    global pas
    global userId
    userId = request.args.get("id")
    print(id)

    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myCursor.execute(
        "SELECT login, password FROM users where oid='" + str(userId) + "'"
    )
    records = myCursor.fetchone()
    myConnection.commit()

    log = records[0]
    pas = records[1]

    form = LoginForm(formdata=MultiDict({"login": log, "password": pas}))
    return render_template(
        "editAdmin.html", title="Edytowanie", form=form, login=log, password=pas
    )


@app.route("/editData", methods=["POST", "GET"])
def editData():
    global log
    global pas
    login = request.form["login"]
    password = request.form["password"]
    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myCursor.execute(
        "UPDATE users SET login='"
        + login
        + "', password='"
        + password
        + "' where login='"
        + log
        + "';"
    )
    myConnection.commit()

    flash("Edytowano")
    log = login
    pas = password
    return render_template("saveData.html", title="Edytowano")


@app.route("/editDataAdmin", methods=["POST", "GET"])
def editDataAdmin():
    global log
    global pas
    global userId
    login = request.form["login"]
    password = request.form["password"]
    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myCursor.execute(
        "UPDATE users SET login='"
        + login
        + "', password='"
        + password
        + "' where oid='"
        + str(userId)
        + "';"
    )
    myConnection.commit()

    flash("Edytowano")
    log = login
    pas = password
    myCursor.execute("SELECT *, oid FROM users")
    records = myCursor.fetchall()
    myConnection.commit()
    return render_template("adminHome.html", title="Edytowano", records=records)


@app.route("/home")
def home():
    return render_template("saveData.html", title="Home")


@app.route("/homeAdmin")
def homeAdmin():
    myConnection = sqlite3.connect("users.sqlite")
    myCursor = myConnection.cursor()
    myCursor.execute("SELECT *, oid FROM users")
    records = myCursor.fetchall()
    myConnection.commit()
    return render_template("adminHome.html", title="Home Admin", records=records)


@app.errorhandler(404)
def pageNotFound(error):
    return render_template("404.html", title="Error 404"), 404


@app.errorhandler(500)
def internalServerError(error):
    return render_template("500.html", title="Error 500"), 500


if __name__ == "__main__":
    app.run(debug=True)

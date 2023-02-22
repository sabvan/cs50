"""
My Personal Diary
Sabrina Van
Fredericksburg, VA, USA

"""

import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

#from helpers import apology, login_required, lookup, usd

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///accounts.db")

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username"):
            return render_template("fix.html", fix="INSERT A USERNAME")
        elif not request.form.get("password"):
            return render_template("fix.html", fix="INSERT A PASSWORD")

        rows = db.execute("SELECT * FROM accounts WHERE username = :username",username=request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return render_template("fix.html", fix="INVALID USERNAME OR PASSWORD")

        session["user_id"] = rows[0]["id"]
        return redirect("/loggedin")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    else:
        namee = db.execute("SELECT * FROM accounts WHERE username = :username",username=request.form.get("username"))

        if not request.form.get("username"):
            return render_template("fix.html", fix="YOU NEED TO INSERT A USERNAME")

        elif request.form.get("username") == namee:
            return render_template("fix.html", fix="THIS USERNAME IS ALREADY TAKEN")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("fix.html", fix="YOU NEED TO INSERT A PASSWORD")

        elif not request.form.get("confirmation"):
            return render_template("fix.html", fix="YOU NEED TO CONFIRM PASSWORD")

        else:
            username = request.form.get("username")
            password = request.form.get("password")
            confirmpassword = request.form.get("confirmation")

            if password != confirmpassword:
                return render_template("fix.html", fix="PASSWORDS ARE NOT THE SAME")
            else:
                hashes = generate_password_hash(request.form.get("password"))
                rows = db.execute("INSERT INTO accounts (username, password) VALUES (:username, :password)", username=username, password=hashes)
                return redirect("/")

@app.route("/loggedin")
def loggedin():
    return render_template("loggedin.html")

@app.route("/relax")
def relax():
    return render_template("relax.html")

@app.route("/dailycheck", methods=["GET", "POST"])
def dailycheck():
    if request.method == "GET":
        return render_template("dailycheck.html")
    else:
        # check if there are missing inputs
        if not request.form.get("mentally"):
            return render_template("fix.html", fix="YOU NEED TO SELECT A VALUE FOR THE MENTAL HEALTH QUESTION")

        elif not request.form.get("mentalinput"):
            return render_template("fix.html", fix="YOU NEED TO WRITE HOW YOU ARE FEELING MENTALLY")

        elif not request.form.get("socially"):
            return render_template("fix.html", fix="YOU NEED TO SELECT A VALUE FOR THE SOCIAL INTERACTION QUESTION")

        elif not request.form.get("socialinput"):
            return render_template("fix.html", fix="YOU NEED TO WRITE HOW YOUR SOCIAL INTERACTIONS WERE")

        elif not request.form.get("physically"):
            return render_template("fix.html", fix="YOU NEED TO SELECT A VALUE FOR THE PHYSICAL HEALTH QUESTION")

        elif not request.form.get("physicalinput"):
            return render_template("fix.html", fix="YOU NEED TO WRITE HOW YOU ARE FEELING PHYSICALLY")

        elif not request.form.get("eating"):
            return render_template("fix.html", fix="YOU NEED TO SELECT A VALUE FOR THE EATING QUESTION")

        elif not request.form.get("eatinginput"):
            return render_template("fix.html", fix="YOU NEED TO WRITE HOW YOU ARE TODAY")

        elif not request.form.get("anythinginput"):
            return render_template("fix.html", fix="YOU NEED TO WRITE DOWN YOUR RANDOM THOUGHTS")

        else:
            mental = int(request.form.get("mentally"))
            social = int(request.form.get("socially"))
            physical = int(request.form.get("physically"))
            eat = int(request.form.get("eating"))

            wellness = round(((mental - 1) * 6.25) + ((social - 1) * 6.25) + ((physical - 1) * 6.25) + ((eat - 1) * 6.25))

            db.execute("""
            INSERT INTO entries(id, mentally, mentalinput, socially, socialinput, physically, physicalinput, eating, eatinginput, anythinginput, wellnesspoints)
            VALUES(:id, :mentally, :mentalinput, :socially, :socialinput, :physically, :physicalinput, :eating, :eatinginput, :anythinginput, :wellnesspoints)""",
            id=session["user_id"], mentally=mental, mentalinput=request.form.get("mentalinput"), socially=social, socialinput=request.form.get("socialinput"), physically=physical, physicalinput=request.form.get("physicalinput"), eating=eat, eatinginput=request.form.get("eatinginput"), anythinginput=request.form.get("anythinginput"), wellnesspoints=wellness)


            return redirect("/diary")
# mentally, mentalinput, socially, socialinput, physically, physicalinput, eating, eatinginput, anythinginput


@app.route("/diary")
def diary():
    rows = db.execute("SELECT * FROM entries WHERE id=:id", id=session["user_id"])

    tablets = []

    for row in rows:
        tablets.append({"mt": row["mentally"], "mti": row["mentalinput"], "sc": row["socially"], "sci": row["socialinput"], "phy": row["physically"], "phyi": row["physicalinput"], "ea": row["eating"], "eati": row["eatinginput"], "anyt": row["anythinginput"], "date": row["dateentered"], "well": row["wellnesspoints"] })

    return render_template("diary.html", tablets = tablets)


@app.route("/account")
def account():
    account = db.execute("SELECT username, datejoined FROM accounts WHERE id=:id", id=session["user_id"])
    username = account[0]["username"]
    joined = account[0]["datejoined"]

    rows = db.execute("SELECT wellnesspoints FROM entries WHERE id=:id", id=session["user_id"])
    avwellness = 0
    counter = 0

    for row in rows:
        temp = int(row["wellnesspoints"])
        avwellness += temp
        counter += 1

    avwellness = round(avwellness / counter)

    return render_template("account.html", username=username, joined=joined, avwellness=avwellness, counter=counter)


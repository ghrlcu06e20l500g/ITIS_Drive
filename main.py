from flask import *
import sqlite3
import string
import random


from routes.settings import *

import query


app = Flask(__name__)
app.secret_key = "thisisasupersecretvalue"

app.register_blueprint(settings_blueprint)

@app.route("/")
def index():
    return redirect(url_for("home"))
@app.route("/home")
def home():
    return render_template("home.html", user = session.get("user"))

@app.route("/drive")
def drive():
    return render_template("drive.html", user = session.get("user"))
@app.route("/drive/add")
def drive_add():
    print("AAAAAAAAAAAAAAAAA")
    return render_template("drive.html", user = session.get("user"))

@app.route("/login")
def login():
    return render_template("login.html", message = None)
@app.route("/login/send_credentials", methods=["POST"])
def send_credentials():
    username = request.form['username']
    password = request.form['password']

    user = query.run("SELECT * FROM users WHERE username=\"{username}\"", query.Mode.FETCH_ONE)

    if user is not None:
        if user["password"] == password:
            session["user"] = {"username": user["username"], "password": password} 
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message = "Wrong password.")
    else:
        query.run(f"INSERT INTO users(username, password) VALUES(\"{username}\", \"{password}\")")
        session["user"] = {"username": username, "password": password} 
        return redirect(url_for("home"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)

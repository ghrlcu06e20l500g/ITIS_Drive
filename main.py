from flask import *
import sqlite3
import string
import random

from routes.settings import *

app = Flask(__name__)
app.secret_key = "thisisasupersecretvalue"

app.register_blueprint(settings_blueprint)

@app.route("/")
def index():
    return redirect(url_for("home"))
@app.route("/home")
def home():
    return render_template("home.html", user = session.get("user"))

@app.route("/login")
def login():
    return render_template("login.html", message = None)
@app.route("/login/login_credentials_post", methods=["POST"])
def login_credentials_post():
    username = request.form['username']
    password = request.form['password']

    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()
    cursor.row_factory = sqlite3.Row

    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if user is not None:
        if user["password"] == password:
            session["user"] = {"username": user["username"], "password": password} 
            return redirect(url_for("home"))
        else:
            return render_template("login.html", message = "Wrong password.")
    else:
        cursor.execute("INSERT INTO users(username, password) VALUES(?, ?)", (username, password, ))
        connection.commit()
        session["user"] = {"username": username, "password": password} 
        return redirect(url_for("home"))

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
